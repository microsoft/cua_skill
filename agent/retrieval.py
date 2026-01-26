import json
import numpy as np
from typing import List, Dict, Any, Tuple, Optional, Set
from sentence_transformers import SentenceTransformer
import nltk
from nltk.tokenize import word_tokenize
from pathlib import Path
from collections import Counter
import math
import pandas as pd
import torch
import importlib
import pkgutil
import re
import logging
from .action.base_action import _OP_REGISTRY as GLOBAL_ACTION_REGISTRY
from .action.base_action import EXECUTABLE_ACTIONS
from . import action as action_package
from .utils import LogMessage  # Add this import


class BM25:
    """Custom BM25 implementation for document ranking"""

    def __init__(self, corpus: List[List[str]], k1: float = 0.5, b: float = 0.5, delta: float = 0.):
        """
        Initialize BM25 with corpus
        
        Args:
            corpus: List of tokenized documents
            k1: Term frequency saturation parameter (default: 0.5)
            b: Length normalization parameter (default: 0.0)
            delta: Parameter for BM25+ variant (default: 0.5)
        """
        self.k1 = k1
        self.b = b
        self.delta = delta
        self.corpus = corpus
        self.corpus_size = len(corpus)
        
        # Calculate document lengths and average
        self.doc_lengths = [len(doc) for doc in corpus]
        self.avgdl = sum(self.doc_lengths) / self.corpus_size if self.corpus_size > 0 else 0
        
        # Calculate document frequencies
        self.doc_freqs = []
        self.df = {}  # Document frequency for each term
        
        for doc in corpus:
            doc_freq = Counter(doc)
            self.doc_freqs.append(doc_freq)
            
            # Update document frequency
            for word in set(doc):
                self.df[word] = self.df.get(word, 0) + 1
        
        # Calculate IDF for all terms
        self.idf = {}
        for word, freq in self.df.items():
            # Correct IDF formula: log((N - df + 0.5) / (df + 0.5) + 1)
            self.idf[word] = math.log(((self.corpus_size - freq + 0.5) / (freq + 0.5)) + 1)

    def get_scores(self, query: List[str]) -> np.ndarray:
        """
        Calculate BM25 scores for all documents given a query
        
        Args:
            query: List of query tokens
            
        Returns:
            Array of BM25 scores for each document
        """
        scores = np.zeros(self.corpus_size)
        
        # Get query term frequencies
        query_freq = Counter(query)
        
        for idx in range(self.corpus_size):
            doc_score = 0.0
            doc_len = self.doc_lengths[idx]
            doc_freqs = self.doc_freqs[idx]
            
            for term, q_freq in query_freq.items():
                if term not in self.idf:
                    # Term not in corpus
                    continue
                
                # Get term frequency in document
                tf = doc_freqs.get(term, 0)
                
                # Calculate BM25+ score component for this term
                # According to Wikipedia formula: IDF * [(f(qi,D) * (k1+1)) / (f(qi,D) + k1 * (1-b+b*|D|/avgdl)) + delta]
                denominator = tf + self.k1 * (1 - self.b + self.b * (doc_len / self.avgdl))
                
                if denominator > 0:
                    tf_component = (tf * (self.k1 + 1)) / denominator + self.delta
                else:
                    tf_component = self.delta
                
                # Add IDF-weighted score
                doc_score += self.idf[term] * tf_component * q_freq
            
            scores[idx] = doc_score
        
        return scores
    
    def get_top_k(self, query: List[str], k: int = 5) -> List[Tuple[int, float]]:
        """
        Get top-k documents for a query
        
        Args:
            query: List of query tokens
            k: Number of top documents to retrieve
            
        Returns:
            List of tuples (document_index, score)
        """
        scores = self.get_scores(query)
        top_indices = np.argsort(scores)[-k:][::-1]
        return [(int(idx), float(scores[idx])) for idx in top_indices]


class HybridIndexer:
    """Indexer class that creates both semantic and BM25 indices for documents"""
    
    def __init__(self, index_dir: str = "./indices", model_name: str = "Qwen/Qwen3-Embedding-0.6B", logger=None):
        """
        Initialize the hybrid indexer
        
        Args:
            index_dir: Directory to store index files
            model_name: Name of the sentence transformer model
        """
        try:
            nltk.data.find("tokenizers/punkt_tab")
        except LookupError:
            nltk.download("punkt_tab")
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize semantic model
        self.semantic_model = SentenceTransformer(model_name)
        
        # Paths for index files
        self.semantic_index_path = self.index_dir / "semantic_index.json"
        self.bm25_index_path = self.index_dir / "bm25_index.json"
        self.documents_path = self.index_dir / "documents.json"
        if logger is None:
            logging.basicConfig(level=logging.INFO)
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logger

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text for BM25"""
        return word_tokenize(text.lower())
    
    def _load_existing_indices(self) -> Tuple[Optional[Dict], Optional[Dict], Optional[Dict]]:
        """
        Load existing index files if they exist
        
        Returns:
            Tuple of (semantic_data, bm25_data, doc_data) or None for each if not exists
        """
        semantic_data = None
        bm25_data = None
        doc_data = None
        
        if self.semantic_index_path.exists():
            with open(self.semantic_index_path, 'r') as f:
                semantic_data = json.load(f)
                self.logger.info(
                    LogMessage(
                        type="HybridIndexer._load_existing_indices",
                        message=f"Loaded existing semantic index with {semantic_data['num_documents']} documents"
                    )
                )
                
        if self.bm25_index_path.exists():
            with open(self.bm25_index_path, 'r') as f:
                bm25_data = json.load(f)
                self.logger.info(
                    LogMessage(
                        type="HybridIndexer._load_existing_indices",
                        message="Loaded existing BM25 index"
                    )
                )
                
        if self.documents_path.exists():
            with open(self.documents_path, 'r') as f:
                doc_data = json.load(f)
                self.logger.info(
                    LogMessage(
                        type="HybridIndexer._load_existing_indices",
                        message=f"Loaded existing documents index with {len(doc_data.get('document_ids', []))} documents"
                    )
                )
                
        return semantic_data, bm25_data, doc_data
    
    def index_documents(self, documents: Dict[str, str], overwrite: bool = False):
        """
        Index documents using both semantic and BM25 approaches
        
        Args:
            documents: Dictionary with document IDs as keys and document texts as values
            overwrite: If True, overwrite existing index. If False, append to existing index
        """
        if not documents:
            self.logger.warning(
                LogMessage(
                    type="HybridIndexer.index_documents",
                    message="No documents provided for indexing"
                )
            )
            return
        
        # Load existing indices if not overwriting
        existing_doc_ids = set()
        existing_documents_dict = {}
        
        if not overwrite and any([self.semantic_index_path.exists(), 
                                  self.bm25_index_path.exists(), 
                                  self.documents_path.exists()]):
            self.logger.info(
                LogMessage(
                    type="HybridIndexer.index_documents",
                    message="Loading existing indices"
                )
            )
            semantic_data, bm25_data, doc_data = self._load_existing_indices()
            
            if doc_data:
                # Build dictionary of existing documents
                existing_doc_ids = set(doc_data.get("document_ids", []))
                existing_docs_list = doc_data.get("documents", [])
                existing_ids_list = doc_data.get("document_ids", [])
                existing_documents_dict = {doc_id: doc for doc_id, doc in zip(existing_ids_list, existing_docs_list)}
        else:
            if overwrite:
                self.logger.info(
                    LogMessage(
                        type="HybridIndexer.index_documents",
                        message="Overwriting existing indices"
                    )
                )
            else:
                self.logger.info(
                    LogMessage(
                        type="HybridIndexer.index_documents",
                        message="Creating new indices"
                    )
                )
            semantic_data = None
            bm25_data = None
            doc_data = None
        
        # Filter out documents that already exist (if not overwriting)
        new_documents_dict = {}
        skipped_count = 0
        
        if not overwrite:
            for doc_id, doc_text in documents.items():
                if doc_id not in existing_doc_ids:
                    new_documents_dict[doc_id] = doc_text
                else:
                    skipped_count += 1
            
            if skipped_count > 0:
                self.logger.info(
                    LogMessage(
                        type="HybridIndexer.index_documents",
                        message=f"Skipped {skipped_count} documents that already exist in the index"
                    )
                )
            
            if len(new_documents_dict) == 0:
                self.logger.info(
                    LogMessage(
                        type="HybridIndexer.index_documents",
                        message="No new documents to index"
                    )
                )
                return

            self.logger.info(
                LogMessage(
                    type="HybridIndexer.index_documents",
                    message=f"Adding {len(new_documents_dict)} new documents to existing index of {len(existing_doc_ids)} documents"
                )
            )
        else:
            new_documents_dict = documents
            self.logger.info(
                LogMessage(
                    type="HybridIndexer.index_documents",
                    message=f"Indexing {len(new_documents_dict)} documents"
                )
            )

        # Merge with existing documents
        all_documents_dict = existing_documents_dict.copy() if not overwrite else {}
        all_documents_dict.update(new_documents_dict)
        
        # Convert to lists for processing (maintaining order)
        all_document_ids = list(all_documents_dict.keys())
        all_documents = list(all_documents_dict.values())
        new_document_ids = list(new_documents_dict.keys())
        new_documents = list(new_documents_dict.values())
        
        # Create semantic embeddings
        self.logger.info(
            LogMessage(
                type="HybridIndexer.index_documents",
                message="Creating semantic embeddings..."
            )
        )
        if semantic_data and not overwrite and len(existing_doc_ids) > 0:
            # Load existing embeddings and add new ones
            existing_embeddings = np.array(semantic_data["embeddings"])
            new_embeddings = self.semantic_model.encode(new_documents)
            semantic_embeddings = np.vstack([existing_embeddings, new_embeddings])
        else:
            # Create all embeddings from scratch
            semantic_embeddings = self.semantic_model.encode(all_documents)
        
        # Create BM25 index for all documents (needs to be rebuilt completely for correct IDF)
        self.logger.info(
            LogMessage(
                type="HybridIndexer.index_documents",
                message="Creating BM25 index..."
            )
        )
        all_tokenized_docs = [self._tokenize(doc) for doc in all_documents]
        bm25_index = BM25(all_tokenized_docs)
        
        # Save semantic embeddings as JSON
        self.logger.info(
            LogMessage(
                type="HybridIndexer.index_documents",
                message="Saving indices..."
            )
        )
        semantic_data = {
            "embeddings": semantic_embeddings.tolist(),
            "embedding_dim": semantic_embeddings.shape[1],
            "num_documents": len(all_documents)
        }
        with open(self.semantic_index_path, 'w') as f:
            json.dump(semantic_data, f, indent=2)
        
        # Save BM25 parameters as JSON
        bm25_data = {
            "corpus": all_tokenized_docs,
            "corpus_size": bm25_index.corpus_size,
            "avgdl": bm25_index.avgdl,
            "doc_lengths": bm25_index.doc_lengths,
            "doc_freqs": [dict(freq) for freq in bm25_index.doc_freqs],
            "df": bm25_index.df,
            "idf": bm25_index.idf,
            "k1": bm25_index.k1,
            "b": bm25_index.b,
            "delta": bm25_index.delta
        }
        with open(self.bm25_index_path, 'w') as f:
            json.dump(bm25_data, f, indent=2)
        
        # Save documents and metadata
        doc_data = {
            "documents": all_documents,
            "document_ids": all_document_ids,
            "total_documents": len(all_documents)
        }
        with open(self.documents_path, 'w') as f:
            json.dump(doc_data, f, indent=2)

        self.logger.info(
            LogMessage(
                type="HybridIndexer.index_documents",
                message=f"Indexing Complete - Total documents in index: {len(all_documents)}, New documents added: {len(new_documents_dict)}"
            )
        )

    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the current index"""
        stats = {
            "index_exists": False,
            "num_documents": 0,
            "document_ids": [],
            "index_dir": str(self.index_dir)
        }
        
        if self.documents_path.exists():
            with open(self.documents_path, 'r') as f:
                doc_data = json.load(f)
                stats["index_exists"] = True
                stats["num_documents"] = doc_data.get("total_documents", 0)
                stats["document_ids"] = doc_data.get("document_ids", [])
        
        return stats

class HybridRetrieval:
    """Retrieval class that combines semantic and BM25 scores for hybrid search"""
    
    def __init__(self, index_dir: str = "./indices", model_name: str = "intfloat/e5-base-v2",
                 semantic_weight: float = 0.5):
        """
        Initialize the hybrid retrieval system
        
        Args:
            index_dir: Directory containing index files
            model_name: Name of the sentence transformer model
            semantic_weight: Weight for semantic scores (1 - semantic_weight for BM25)
        """
        self.index_dir = Path(index_dir)
        self.semantic_weight = semantic_weight
        self.bm25_weight = 1 - semantic_weight
        
        # Initialize semantic model
        self.semantic_model = SentenceTransformer(model_name)
        
        # Load indices
        self._load_indices()
        
    def _load_indices(self):
        """Load pre-built indices from disk"""
        # Check if all required files exist
        required_files = [
            self.index_dir / "semantic_index.json",
            self.index_dir / "bm25_index.json",
            self.index_dir / "documents.json"
        ]
        
        for file_path in required_files:
            if not file_path.exists():
                raise FileNotFoundError(f"Required index file not found: {file_path}")
        
        # Load semantic embeddings from JSON
        with open(self.index_dir / "semantic_index.json", 'r') as f:
            semantic_data = json.load(f)
            self.semantic_embeddings = np.array(semantic_data["embeddings"])
        
        # Load BM25 index from JSON and reconstruct
        with open(self.index_dir / "bm25_index.json", 'r') as f:
            bm25_data = json.load(f)
            
        # Reconstruct BM25 object
        self.bm25_index = BM25(bm25_data["corpus"], 
                               k1=bm25_data["k1"], 
                               b=bm25_data["b"], 
                               delta=bm25_data["delta"])
        
        # Restore pre-computed values to avoid recalculation
        self.bm25_index.avgdl = bm25_data["avgdl"]
        self.bm25_index.doc_lengths = bm25_data["doc_lengths"]
        self.bm25_index.doc_freqs = [Counter(freq) for freq in bm25_data["doc_freqs"]]
        self.bm25_index.df = bm25_data["df"]
        self.bm25_index.idf = bm25_data["idf"]
        
        # Load documents and metadata
        with open(self.index_dir / "documents.json", 'r') as f:
            doc_data = json.load(f)
            self.documents = doc_data["documents"]
            self.document_ids = doc_data["document_ids"]
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text for BM25"""
        return word_tokenize(text.lower())
    
    def _normalize_semantic_scores(self, scores: np.ndarray) -> np.ndarray:
        """
        Normalize semantic similarity scores to [0, 1] range
        
        Args:
            scores: Array of semantic similarity scores
            
        Returns:
            Normalized scores in [0, 1] range
        """
        # Check if scores are already in valid [0, 1] range
        max_score = np.max(scores)
        min_score = 0
        
        if max_score > 1 or min_score < 0:
            raise ValueError(f"Semantic scores out of expected [0, 1] range. "
                           f"Min: {min_score:.4f}, Max: {max_score:.4f}")
        
        # Return original scores as they are already normalized
        return scores
    
    def _normalize_bm25_scores(self, scores: np.ndarray, min_cap: float = 0, max_cap: float = 50) -> np.ndarray:
        """
        Normalize BM25 scores to [min_cap, max_cap] range with capping
        
        Args:
            scores: Array of BM25 scores
            min_cap: Minimum cap value (default: 0)
            max_cap: Maximum cap value (default: 10)
            
        Returns:
            Normalized scores in [min_cap, max_cap] range then scaled to [0, 1]
        """
        # Cap scores at max_cap
        normalized = np.minimum(scores, max_cap)
        # Ensure non-negative (at least min_cap)
        normalized = np.maximum(normalized, min_cap)
        # Scale to [0, 1] for combination with semantic scores
        return (normalized - min_cap) / (max_cap - min_cap)

    def retrieve(self, query: str, top_k: int = 5):
        """
        Retrieve top-k documents using hybrid scoring and return as pandas DataFrame
        
        Args:
            query: Query string
            top_k: Number of top documents to retrieve
            
        Returns:
            pandas DataFrame containing document info and scores, ranked by hybrid score
        """
        
        # Calculate semantic similarity scores
        query_embedding = self.semantic_model.encode(query, convert_to_tensor=True, prompt_name="query")
        # Convert numpy embeddings to tensor for similarity calculation
        semantic_embeddings_tensor = torch.from_numpy(self.semantic_embeddings).float()
        
        # Ensure both tensors are on the same device
        semantic_embeddings_tensor = semantic_embeddings_tensor.to(query_embedding.device)
        
        semantic_scores = self.semantic_model.similarity(query_embedding, semantic_embeddings_tensor)
        semantic_scores = semantic_scores.cpu().numpy().flatten()
        
        # Calculate BM25 scores
        tokenized_query = self._tokenize(query)
        bm25_scores = self.bm25_index.get_scores(tokenized_query)
        
        # Normalize scores with different strategies
        semantic_scores_norm = self._normalize_semantic_scores(semantic_scores)
        bm25_scores_norm = self._normalize_bm25_scores(bm25_scores)
        
        # Calculate weighted hybrid scores
        hybrid_scores = (self.semantic_weight * semantic_scores_norm + 
                        self.bm25_weight * bm25_scores_norm)
        
        # Get top-k indices
        top_indices = np.argsort(hybrid_scores)[-top_k:][::-1]
        
        # Create DataFrame
        df_data = []
        for rank, idx in enumerate(top_indices, 1):
            df_data.append({
                'rank': rank,
                'document_id': self.document_ids[idx],
                'document': self.documents[idx],
                'bm25_score_raw': float(bm25_scores[idx]),
                'semantic_score_raw': float(semantic_scores[idx]),
                'bm25_score_norm': float(bm25_scores_norm[idx]),
                'semantic_score_norm': float(semantic_scores_norm[idx]),
                'hybrid_score': float(hybrid_scores[idx])
            })
        
        df = pd.DataFrame(df_data)
        
        # Set column order
        column_order = [
            'rank',
            'document_id',
            'document',
            'bm25_score_raw',
            'semantic_score_raw',
            'bm25_score_norm',
            'semantic_score_norm',
            'hybrid_score'
        ]
        
        return df[column_order]
    
    def update_weights(self, semantic_weight: float):
        """
        Update the weights for hybrid scoring
        
        Args:
            semantic_weight: New weight for semantic scores
        """
        self.semantic_weight = semantic_weight
        self.bm25_weight = 1 - semantic_weight


class ActionRetriever(HybridRetrieval):

    def __init__(self, index_dir: str = "rag_cua/rag_index/actions", model_name: str = "Qwen/Qwen3-Embedding-0.6B",
                 semantic_weight: float = 0.5, overwrite: bool = False, logger=None, sample_action_path: Optional[str] = None):
        if logger is None:
            logging.basicConfig(level=logging.INFO)
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logger
        if sample_action_path:
            self.allowed_action_types = json.load(open(sample_action_path, "r"))
        else:
            self.allowed_action_types = None

        self.indexer = HybridIndexer(index_dir=index_dir, model_name=model_name, logger=self.logger)
        self.build_index(overwrite=overwrite)
        super().__init__(index_dir=index_dir, model_name=model_name, semantic_weight=semantic_weight)

    def force_reset_logger(self, logger):
        self.logger = logger
        self.indexer.logger = logger

    def build_index(self, overwrite: bool = False):
        """
        Build or update the action index by extracting descriptions from registered actions.

        Args:
            overwrite: If True, overwrite existing index. If False, append to existing index
        """
        
        self.logger.info(
            LogMessage(
                type="ActionRetriever.build_index",
                message="Building Action Index"
            )
        )
        action_documents = self.extract_all_action_descriptions()
        self.logger.info(
            LogMessage(
                type="ActionRetriever.build_index",
                message=f"Total actions to index: {len(action_documents)}"
            )
        )

        if len(action_documents) == 0:
            self.logger.warning(
                LogMessage(
                    type="ActionRetriever.build_index",
                    message="No action descriptions found to index."
                )
            )
            return
        
        self.indexer.index_documents(action_documents, overwrite=overwrite)
        self.logger.info(
            LogMessage(
                type="ActionRetriever.build_index",
                message="Action index built/updated successfully."
            )
        )



    def extract_all_action_descriptions(self) -> Dict[str, str]:
        """
        Extract descriptions from all registered actions in the agent.action directory.
        
        Returns:
            Dictionary with action names as keys and concatenated descriptions as values
        """
        
        for importer, modname, ispkg in pkgutil.iter_modules(action_package.__path__, 
                                                            prefix=action_package.__name__ + "."):
            if not ispkg and modname.endswith('_action') and not modname.startswith('base_action'):
                try:
                    importlib.import_module(modname)
                    self.logger.debug(
                        LogMessage(
                            type="ActionRetriever.extract_all_action_descriptions",
                            message=f"Imported {modname}"
                        )
                    )
                except Exception as e:
                    self.logger.error(
                        LogMessage(
                            type="ActionRetriever.extract_all_action_descriptions",
                            message=f"Failed to import {modname}: {e}"
                        )
                    )

        action_documents = {}
        
        for action_name, action_class in GLOBAL_ACTION_REGISTRY.items():
            if action_name in EXECUTABLE_ACTIONS:
                continue
            if self.allowed_action_types and action_class.type not in self.allowed_action_types:
                    continue
            if hasattr(action_class, 'descriptions') and action_class.descriptions:
                processed_descriptions = []
                for desc in action_class.descriptions:
                    processed_desc = desc
                    if '{' in desc:
                        processed_desc = re.sub(r'\$\{\{([^}]+)\}\}', lambda m: f"target {m.group(1)}", desc)
                        processed_desc = re.sub(r'\{([^}]+)\}', lambda m: f"target {m.group(1)}", processed_desc)
                    processed_descriptions.append(processed_desc)
            
                for idx, description_text in enumerate(processed_descriptions):
                    # full_text = f"{action_name}\n{action_type}\n{application_name}\n{domain}\n{description_text}"
                    action_type = " ".join(getattr(action_class, 'type', '').split("_"))
                    full_text = f"{action_type}: {description_text}"
                    document_id = f"{action_name}_#ID#_{idx}"
                    action_documents[document_id] = full_text
            else: ## not all actions have descriptions
                # Fallback: use action name and type only
                action_type = " ".join(getattr(action_class, 'type', '').split("_"))
                full_text = f"{action_name}: {action_type}"
                document_id = action_name
                action_documents[document_id] = full_text
                
        
        return action_documents

    def retrieve_actions_df(self, query: str, 
                        top_k: int = 5) -> pd.DataFrame:


        df_results = self.retrieve(query, top_k=5 * top_k)
        
        # self.logger.info(f"Raw retrieval results:\n{df_results[['rank', 'document_id', 'hybrid_score', 'semantic_score_raw', 'bm25_score_raw']]}")
        enhanced_data = []
        
        for idx, row in df_results.iterrows():
            document_id = row['document_id']
            if '_#ID#_'  in document_id:
                action_name = document_id.split('_#ID#_')[0]
                description_id = int(document_id.split('_#ID#_')[1])
            else:
                action_name = document_id
                description_id = 0
            action_class = GLOBAL_ACTION_REGISTRY.get(action_name)
            
            if action_class:
                # Extract metadata
                action_type = getattr(action_class, 'type', 'N/A')
                application_name = getattr(getattr(action_class, 'application_name', 'N/A'), "value", 'N/A')
                descriptions = getattr(action_class, 'descriptions', [])
                description = descriptions[description_id] if description_id < len(descriptions) else 'No description available'
                
                # Create enhanced row
                enhanced_row = {
                    'rank': row['rank'],
                    'action_name': action_name,
                    'action_class': action_class,
                    'action_type': action_type,
                    'description': description,
                    'application_name': application_name,
                    'hybrid_score': row['hybrid_score'],
                    'semantic_score': row['semantic_score_raw'],
                    'bm25_score': row['bm25_score_raw']
                }
                enhanced_data.append(enhanced_row)
        
        # Create enhanced DataFrame
        enhanced_df = pd.DataFrame(enhanced_data)
        enhanced_df = enhanced_df.sort_values(by='hybrid_score', ascending=False).reset_index(drop=True)
        enhanced_df.drop_duplicates(subset=['action_name'], inplace=True)
        enhanced_df = enhanced_df.head(top_k)
        enhanced_df.reset_index(drop=True, inplace=True)
        self.logger.info(
            LogMessage(
                type="ActionRetriever.retrieve_actions_df",
                message=f"retrieved actions:\n{enhanced_df[['rank', 'action_name', 'hybrid_score']]}"
            )
        )
        return enhanced_df
    
    def retrieve_actions(self, query: str, 
                        top_k: int = 5) -> List:
        out_df = self.retrieve_actions_df(query, top_k=top_k)
        res = out_df["action_class"].tolist()
        return res
        

if __name__ == "__main__":
    # Set up logging for testing
    logging.basicConfig(level=logging.INFO)
    
    # Create an ActionRetriever instance
    action_retriever = ActionRetriever(semantic_weight=0.7)
    
    # Test extracting all action descriptions
    print("Extracting All Action Descriptions")
    all_actions = action_retriever.extract_all_action_descriptions()
    print(f"Total actions found: {len(all_actions)}")
    
    # Test retrieval with different queries
    test_queries = [
    "Use keyboard entry: enter 398-174*√(505) and press Enter"
    ]

    print("Testing Action Retrieval")
    for query in test_queries:
        print(f"Query: '{query}'")
        
        # Retrieve actions
        results_df = action_retriever.retrieve_actions_df(query, top_k=3)
        
        # Display results
        if not results_df.empty:
            for idx, row in results_df.iterrows():
                print(f"{row['rank']}. {row['action_name']} - "
                          f"Type: {row['action_type']}, "
                          f"Description: {row['description']}, "
                          f"Scores - Hybrid: {row['hybrid_score']:.3f}, "
                          f"Semantic: {row['semantic_score']:.3f}, "
                          f"BM25: {row['bm25_score']:.3f}")
        else:
            print("No results found")
