import random
from typing import Optional, Sequence, Union, Dict, Any, Iterable

# Comprehensive product database with categories and variations
_PRODUCTS: Dict[str, Sequence[str]] = {
    "electronics": [
        "laptop stand", "wireless mouse", "USB-C hub", "Bluetooth headphones",
        "external hard drive", "4K monitor", "gaming keyboard", "smartwatch",
        "fitness tracker", "noise-cancelling earbuds", "portable charger",
        "webcam", "mechanical keyboard", "graphic tablet", "action camera",
        "drone", "smart home hub", "e-reader", "VR headset", "streaming device",
        "wireless router", "smart thermostat", "home security camera",
        "smart doorbell", "wireless earbuds", "tablet", "smartphone",
        "laptop", "desktop computer", "printer", "scanner", "USB flash drive",
        "memory card", "HDMI cable", "power bank", "bluetooth speaker",
        "smart TV", "soundbar", "projector", "gaming console", "microphone"
    ],
    "home_appliances": [
        "robot vacuum", "air purifier", "humidifier", "dehumidifier",
        "space heater", "tower fan", "coffee maker", "espresso machine",
        "blender", "air fryer", "instant pot", "slow cooker", "toaster oven",
        "microwave", "dishwasher", "refrigerator", "washing machine", "dryer",
        "vacuum cleaner", "steam cleaner", "pressure washer", "food processor",
        "electric kettle", "rice cooker", "bread maker", "juicer", "mixer"
    ],
    "furniture": [
        "standing desk", "office chair", "bookshelf", "desk lamp",
        "monitor stand", "filing cabinet", "desk organizer", "ergonomic chair",
        "coffee table", "side table", "dining table", "sofa", "recliner",
        "bed frame", "mattress", "nightstand", "dresser", "wardrobe",
        "shoe rack", "storage ottoman", "TV stand", "bar stool"
    ],
    "fitness": [
        "yoga mat", "dumbbell set", "resistance bands", "jump rope",
        "foam roller", "massage gun", "exercise bike", "treadmill",
        "rowing machine", "elliptical", "weight bench", "pull-up bar",
        "kettlebell", "medicine ball", "balance board", "fitness ball",
        "ankle weights", "gym gloves", "workout mat", "protein shaker"
    ],
    "outdoor": [
        "camping tent", "sleeping bag", "hiking backpack", "water bottle",
        "camping stove", "cooler", "folding chair", "hammock", "lantern",
        "grill", "patio furniture set", "outdoor umbrella", "fire pit",
        "garden hose", "lawn mower", "leaf blower", "pressure washer",
        "bike", "electric scooter", "skateboard", "helmet"
    ],
    "clothing": [
        "running shoes", "winter jacket", "rain jacket", "jeans",
        "t-shirt", "sweater", "dress shirt", "suit", "dress", "skirt",
        "shorts", "leggings", "socks", "underwear", "belt", "tie",
        "scarf", "gloves", "hat", "sunglasses", "watch", "backpack"
    ],
    "beauty": [
        "face moisturizer", "sunscreen", "lip balm", "shampoo",
        "conditioner", "body wash", "face wash", "serum", "face mask",
        "hair dryer", "curling iron", "straightener", "electric toothbrush",
        "razor", "beard trimmer", "nail kit", "makeup brush set"
    ],
    "toys": [
        "LEGO set", "board game", "puzzle", "action figure", "doll",
        "toy car", "train set", "building blocks", "stuffed animal",
        "art supplies", "coloring book", "play dough", "remote control car",
        "drone toy", "science kit", "musical toy", "educational toy"
    ],
    "books": [
        "cookbook", "novel", "biography", "self-help book", "travel guide",
        "history book", "science book", "programming book", "art book",
        "children's book", "comic book", "graphic novel", "textbook",
        "dictionary", "encyclopedia", "magazine", "journal", "planner"
    ],
    "kitchen": [
        "cutting board", "knife set", "cookware set", "baking sheet",
        "measuring cups", "mixing bowls", "storage containers", "spice rack",
        "can opener", "vegetable peeler", "kitchen scale", "oven mitts",
        "dish rack", "utensil set", "serving tray", "wine opener"
    ],
    "pet_supplies": [
        "dog food", "cat food", "pet bed", "pet carrier", "leash",
        "collar", "pet toys", "litter box", "scratching post", "pet bowl",
        "grooming kit", "pet shampoo", "flea treatment", "pet treats",
        "aquarium", "bird cage", "hamster wheel", "pet gate"
    ],
    "automotive": [
        "car charger", "phone mount", "dash cam", "jump starter",
        "tire inflator", "car vacuum", "seat covers", "floor mats",
        "steering wheel cover", "air freshener", "windshield wipers",
        "motor oil", "car wash kit", "emergency kit", "tool set"
    ]
}

# Brand names that can be associated with products
_BRANDS: Sequence[str] = [
    "Samsung", "Apple", "Sony", "Dell", "HP", "Lenovo", "Asus", "Acer",
    "Microsoft", "Google", "Amazon", "LG", "Bose", "JBL", "Canon", "Nikon",
    "Logitech", "Razer", "Corsair", "Anker", "Belkin", "TP-Link", "Netgear",
    "Philips", "Dyson", "iRobot", "Instant Pot", "Ninja", "KitchenAid",
    "Cuisinart", "Breville", "Black+Decker", "DeWalt", "Nike", "Adidas",
    "Under Armour", "North Face", "Patagonia", "Coleman", "Yeti"
]

# Modifiers that can be added to products
_MODIFIERS: Dict[str, Sequence[str]] = {
    "quality": ["premium", "professional", "deluxe", "basic", "standard", "pro"],
    "size": ["mini", "compact", "portable", "large", "XL", "small"],
    "tech": ["smart", "wireless", "bluetooth", "USB-C", "digital", "electric"],
    "material": ["aluminum", "stainless steel", "bamboo", "leather", "plastic", "wooden"],
    "color": ["black", "white", "silver", "grey", "blue", "red", "green"],
    "generation": ["2024", "2025", "latest", "new", "upgraded", "v2", "gen 3"]
}

def generate_product_name(
    categories: Optional[Iterable[str]] = None,
    prefer_categories: Optional[Iterable[str]] = None,
    include_brand: bool = False,
    include_modifier: bool = False,
    modifier_types: Optional[Sequence[str]] = None,
    complexity: str = "simple",
    as_dict: bool = False,
    seed: Optional[int] = None,
) -> Union[str, Dict[str, Any]]:
    """
    Generate realistic product names for e-commerce scenarios.
    
    Args:
        categories: Restrict to these categories (e.g., ["electronics", "furniture"])
        prefer_categories: Bias sampling toward these categories
        include_brand: Whether to include a brand name
        include_modifier: Whether to include modifiers (adjectives)
        modifier_types: Which modifier types to use (from _MODIFIERS keys)
        complexity: "simple" (base product), "moderate" (+ brand OR modifier), 
                   "complex" (brand + modifier + product)
        as_dict: Return dict with metadata instead of string
        seed: Random seed for reproducibility
        
    Returns:
        Product name string or dict with product details
    """
    rng = random.Random(seed)
    
    # Select category
    available_categories = list(_PRODUCTS.keys())
    if categories:
        available_categories = [c for c in categories if c in _PRODUCTS]
        if not available_categories:
            available_categories = list(_PRODUCTS.keys())
    
    # Apply category preferences
    if prefer_categories:
        pref = set(prefer_categories)
        weighted = []
        for cat in available_categories:
            weight = 3 if cat in pref else 1
            weighted.extend([cat] * weight)
        available_categories = weighted
    
    category = rng.choice(available_categories)
    base_product = rng.choice(_PRODUCTS[category])
    
    # Determine complexity level
    if complexity == "simple":
        include_brand = False
        include_modifier = False
    elif complexity == "moderate":
        # Randomly choose one enhancement
        if rng.random() < 0.5:
            include_brand = True
            include_modifier = False
        else:
            include_brand = False
            include_modifier = True
    elif complexity == "complex":
        include_brand = True
        include_modifier = True
    
    # Build product name components
    components = []
    brand = None
    modifiers = []
    
    if include_brand and rng.random() < 0.7:  # 70% chance when requested
        brand = rng.choice(_BRANDS)
        # Only use brand if it makes sense with the product
        if category in ["electronics", "home_appliances", "fitness", "automotive"]:
            components.append(brand)
    
    if include_modifier:
        available_modifier_types = modifier_types or list(_MODIFIERS.keys())
        # Choose 1-2 modifiers
        num_modifiers = rng.choices([1, 2], weights=[0.7, 0.3])[0]
        selected_types = rng.sample(
            [t for t in available_modifier_types if t in _MODIFIERS],
            min(num_modifiers, len(available_modifier_types))
        )
        
        for mod_type in selected_types:
            modifier = rng.choice(_MODIFIERS[mod_type])
            modifiers.append(modifier)
            components.append(modifier)
    
    components.append(base_product)
    
    # Create final product name
    product_name = " ".join(components)
    
    if as_dict:
        return {
            "name": product_name,
            "base_product": base_product,
            "category": category,
            "brand": brand,
            "modifiers": modifiers,
            "components": components
        }
    
    return product_name


def generate_product_variant(
    base_product: str,
    variation_type: str = "random",
    seed: Optional[int] = None
) -> str:
    """
    Generate a variant of an existing product name.
    
    Args:
        base_product: The base product name to create variant from
        variation_type: Type of variation - "color", "size", "model", "bundle", "random"
        seed: Random seed
        
    Returns:
        Product variant string
    """
    rng = random.Random(seed)
    
    variations = {
        "color": ["Black", "White", "Silver", "Blue", "Red", "Green", "Grey"],
        "size": ["Small", "Medium", "Large", "XL", "XXL", "Mini", "Pro", "Max"],
        "model": ["Basic", "Plus", "Pro", "Elite", "Premium", "Standard", "Deluxe"],
        "bundle": ["2-Pack", "3-Pack", "Bundle", "Kit", "Set", "Combo", "Collection"],
        "generation": ["2024", "2025", "Gen 2", "Gen 3", "v2.0", "Latest", "New"]
    }
    
    if variation_type == "random":
        variation_type = rng.choice(list(variations.keys()))
    
    if variation_type in variations:
        variant = rng.choice(variations[variation_type])
        return f"{base_product} - {variant}"
    
    return base_product


def get_related_products(
    product_name: str,
    num_products: int = 3,
    seed: Optional[int] = None
) -> Sequence[str]:
    """
    Get related/similar products to a given product.
    
    Args:
        product_name: Base product to find related items for
        num_products: Number of related products to return
        seed: Random seed
        
    Returns:
        List of related product names
    """
    rng = random.Random(seed)
    
    # Find the category of the base product
    base_category = None
    base_product_clean = product_name.lower()
    
    for category, products in _PRODUCTS.items():
        for product in products:
            if product.lower() in base_product_clean:
                base_category = category
                break
        if base_category:
            break
    
    if not base_category:
        # Default to electronics if not found
        base_category = "electronics"
    
    # Get products from same category
    related = []
    candidates = [p for p in _PRODUCTS[base_category] if p.lower() != base_product_clean]
    
    if len(candidates) >= num_products:
        related = rng.sample(candidates, num_products)
    else:
        related = candidates[:]
        # Add from other categories if needed
        remaining = num_products - len(related)
        other_products = []
        for cat, prods in _PRODUCTS.items():
            if cat != base_category:
                other_products.extend(prods)
        
        if other_products and remaining > 0:
            related.extend(rng.sample(other_products, min(remaining, len(other_products))))
    
    return related[:num_products]