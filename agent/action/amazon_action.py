from typing import Any, Dict, List

from .compose_action import BaseComposeAction
from .base_action import MoveAction, register, SingleClickAction, WaitAction, TypeAction, HotKeyAction
from .argument import Argument
from .microsoft_edge_action import MicrosoftEdgeLaunch
from .common_action import OpenRun

__all__ = []

class AmazonBaseAction(BaseComposeAction):
    domain: Argument = Argument(
        value="amazon",
        description="The domain of the action.",
        frozen=True
    )
    application_name: Argument = Argument(
        value="Amazon",
        description="The name of the Amazon application.",
        frozen=True
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

@register("AmazonLaunch")
class AmazonLaunch(AmazonBaseAction):
    # Canonical identifiers
    type: str = "amazon_launch"
    
    # Schema payload
    descriptions: List[str] = [
        "Go to Amazon.",
        "Open Amazon.",
        "Find something on Amazon.",
        "Navigate to Amazon.",
        "Go to the Amazon homepage."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "amazon_launch",
            path=[
                MicrosoftEdgeLaunch(),
                WaitAction(duration=2.0),
                SingleClickAction(thought="Click on the address bar"),
                WaitAction(duration=1.0),
                TypeAction(text="https://www.amazon.com", input_mode="copy_paste", thought="Navigate to Amazon homepage"),
                WaitAction(duration=2.0),
                HotKeyAction(keys=["enter"], thought="Press Enter to go to the site"),
                WaitAction(duration=5.0)
            ]
        )
        self.add_path(
            "amazon_launch_run",
            path=[
                OpenRun(thought=f"Open the Run dialog to launch {self.application_name}."),
                WaitAction(duration=1.0),
                TypeAction(text="msedge https://www.amazon.com", input_mode="copy_paste", thought=f"Type command to open Amazon in Microsoft Edge"),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"], thought="Press Enter to run the command"),
                WaitAction(duration=5.0)
            ]
        )


@register("AmazonSearchProduct")
class AmazonSearchProduct(AmazonBaseAction):
    # Canonical identifiers
    type: str = "amazon_search_product"
    query: Argument = Argument(
        value="laptop", 
        description="Search query text to find products on Amazon. Can be a product name, brand, category, model number, or descriptive keywords. Supports natural language queries and specific terms. Examples: 'laptop' (category search), 'iPhone 15 Pro' (specific product), 'wireless headphones under $100' (with criteria), 'Dell XPS 13' (brand and model), 'mechanical keyboard RGB' (multiple keywords), 'kitchen appliances' (broad category), 'Sony WH-1000XM5' (exact model number). The search will return relevant product listings matching the query across Amazon's catalog."
    )

    # Schema payload
    descriptions: List[str] = [
        "Search for ${{query}} on Amazon.",
        "Look up ${{query}}.",
        "Find ${{query}} on Amazon.",
        "Search Amazon for ${{query}}.",
        "Look for ${{query}} in the store."
    ]

    search_box_xy: Dict[str, Any] = {
        "dtype": "tuple",
        "description": "Coordinate of search box.",
        "require_grounding": True
    }

    search_button_xy: Dict[str, Any] = {
        "dtype": "tuple",
        "description": "Coordinate of search button.",
        "require_grounding": True
    }
    
    def __init__(self, query: str = "laptop", **kwargs) -> None:
        super().__init__(query=query, **kwargs)
        self.add_path(
            "amazon_search_product_click_search",
            path=[
                SingleClickAction(thought="Click the search box on Amazon"),
                WaitAction(duration=1.0),
                TypeAction(text=query, input_mode="copy_paste", thought=f"Enter search query '{query}'"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click the search button"),
                WaitAction(duration=2.0)
            ]
        )
        self.add_path(
            "amazon_search_product_hotkey_search",
            path=[
                SingleClickAction(thought="Click the search box on Amazon"),
                WaitAction(duration=1.0),
                TypeAction(text=query, input_mode="copy_paste", thought=f"Enter search query '{query}'"),
                WaitAction(duration=1.0),
                HotKeyAction(keys=["enter"], thought="Press Enter to search"),
                WaitAction(duration=2.0)
            ]
        )

@register("AmazonApplyFilter")
class AmazonApplyFilter(AmazonBaseAction):
    # Canonical identifiers
    type: str = "amazon_apply_filter"
    filter_value: Argument = Argument(
        value="Brand: Apple",
        description="Complete filter specification to narrow down search results on Amazon. Must include both filter category and value in format 'Category: Value'. Common filter categories: 'Brand' (manufacturer name), 'Price' (price range), 'Prime Shipping' (Prime eligible), 'Customer Review' (star ratings), 'Department' (product category), 'Condition' (New/Used/Refurbished), 'Availability' (In Stock/Include Out of Stock). Examples: 'Brand: Apple' (filter by Apple brand), 'Price: $50 to $100' (price range filter), 'Customer Review: 4 Stars & Up' (rating filter), 'Prime Shipping: Prime Eligible' (Prime filter), 'Condition: New' (new items only), 'Department: Electronics' (category filter). The exact text must match the filter option displayed on Amazon's search results page for proper grounding and selection."
    )

    # Schema payload
    descriptions: List[str] = [
        "Filter results by ${{filter_value}}.",
        "Apply ${{filter_value}} filter.",
        "Show only ${{filter_value}}.",
        "Use filter ${{filter_value}}.",
        "Refine results by ${{filter_value}}."
    ]

    def __init__(self, filter_value: str = "Brand: Apple", **kwargs) -> None:
        super().__init__(filter_value=filter_value, **kwargs)
        self.add_path(
            "amazon_apply_filter",
            path=[
                SingleClickAction(thought=f"Select {filter_value} filter option"),
                WaitAction(duration=2.0)
            ]
        )


@register("AmazonSortResults")
class AmazonSortResults(AmazonBaseAction):
    # Canonical identifiers
    type: str = "amazon_sort_results"
    sort_option: Argument = Argument(
        value="Price: Low to High",
        description="Sorting method to reorder Amazon search results. Must match exact text from Amazon's sort dropdown menu. Available sort options: 'Featured' (Amazon's default recommendation algorithm), 'Price: Low to High' (ascending price order, cheapest first), 'Price: High to Low' (descending price order, most expensive first), 'Avg. Customer Review' (highest rated products first), 'Newest Arrivals' (most recently added products first), 'Best Sellers' (most popular items by sales). Examples: 'Price: Low to High' (find cheapest options), 'Avg. Customer Review' (find top-rated products), 'Newest Arrivals' (see latest products), 'Best Sellers' (most popular items). Use exact capitalization and punctuation as shown in Amazon's interface."
    )

    # Schema payload
    descriptions: List[str] = [
        "Sort by ${{sort_option}}.",
        "Order results by ${{sort_option}}.",
        "Change sorting to ${{sort_option}}.",
        "Rearrange by ${{sort_option}}.",
        "Sort Amazon search by ${{sort_option}}."
    ]

    def __init__(self, sort_option: str = "Price: Low to High", **kwargs) -> None:
        super().__init__(sort_option=sort_option, **kwargs)
        self.add_path(
            "amazon_sort_results",
            path=[
                SingleClickAction(thought="Click the sort dropdown"),
                WaitAction(duration=1.0),
                SingleClickAction(thought=f"Select '{sort_option}' from sort options"),
                WaitAction(duration=2.0)
            ]
        )


@register("AmazonOpenProduct")
class AmazonOpenProduct(AmazonBaseAction):
    # Canonical identifiers
    type: str = "amazon_open_product"
    product_name: Argument = Argument(
        value="laptop",
        description="Name or title of the product to open from search results or listings. Should match or closely describe the product title visible on Amazon's interface. Can be full product title or key identifying portion. Examples: 'Apple MacBook Pro 16-inch' (specific product), 'laptop' (generic when multiple similar items), 'Sony WH-1000XM5 Headphones' (brand and model), 'Samsung Galaxy S23 Ultra' (full product name), 'wireless mouse' (product type), 'Kindle Paperwhite' (product line name). This text is used for grounding to identify and click the correct product link on the current page. Use distinctive parts of the product title that uniquely identify it among the visible search results."
    )

    # Schema payload
    descriptions: List[str] = [
        "Open the product ${{product_name}}.",
        "View details for ${{product_name}}.",
        "Check out the product ${{product_name}}.",
        "Open product page for ${{product_name}}.",
        "Show me ${{product_name}} details."
    ]
    
    def __init__(self, product_name: str = "laptop", **kwargs) -> None:
        super().__init__(product_name=product_name, **kwargs)
        self.add_path(
            "amazon_open_product",
            path=[
                SingleClickAction(thought=f"Click on the product '{product_name}' link"),
                WaitAction(duration=2.0)
            ]
        )


@register("AmazonReadReviews")
class AmazonReadReviews(AmazonBaseAction):
    # Canonical identifiers
    type: str = "amazon_read_reviews"
    product_name: Argument = Argument(
        value="laptop",
        description="Name or title of the product whose customer reviews you want to read. Should match the product currently being viewed or the product in the listing. Used for context and grounding to locate the reviews section or link. Examples: 'laptop' (for currently viewed laptop), 'Apple AirPods Pro' (specific product reviews), 'Samsung TV' (brand and type), 'wireless keyboard' (product type). This helps identify which product's reviews to access, especially useful when multiple products are visible on screen or in wishlists/carts."
    )

    # Schema payload
    descriptions: List[str] = [
        "Read reviews for ${{product_name}}.",
        "Show me customer feedback.",
        "Check ratings and reviews.",
        "Look at what people say about ${{product_name}}.",
        "Open reviews section."
    ]
    
    def __init__(self, product_name: str = "laptop", **kwargs) -> None:
        super().__init__(product_name=product_name, **kwargs)
        self.add_path(
            "amazon_read_reviews",
            path=[
                MoveAction(thought="Move to the reviews section and hover"),
                WaitAction(duration=2.0),
                SingleClickAction(thought="Click on the See customer reviews link"),
                WaitAction(duration=2.0)
            ]
        )


@register("AmazonAddToWishlist")
class AmazonAddToWishlist(AmazonBaseAction):
    # Canonical identifiers
    type: str = "amazon_add_to_wishlist"
    product_name: Argument = Argument(
        value="laptop",
        description="Name or title of the product to save to wishlist for future reference. Should match the product currently displayed on the product detail page. Examples: 'laptop' (generic product), 'Dell XPS 13' (specific model), 'wireless headphones' (product type), 'Apple Watch Series 9' (full product name). Adding to wishlist saves the item without purchasing, allowing you to track price changes, share with others, or purchase later. The product must be on a product detail page to add to wishlist."
    )

    # Schema payload
    descriptions: List[str] = [
        "Add ${{product_name}} to wishlist.",
        "Save ${{product_name}} for later.",
        "Put this product in my wishlist.",
        "Bookmark ${{product_name}}.",
        "Add to my saved items."
    ]
    
    def __init__(self, product_name: str = "laptop", **kwargs) -> None:
        super().__init__(product_name=product_name, **kwargs)
        self.add_path(
            "amazon_add_to_wishlist",
            path=[
                SingleClickAction(thought="Click the Add to Wishlist button"),
                WaitAction(duration=1.0)
            ]
        )


@register("AmazonAddToCart")
class AmazonAddToCart(AmazonBaseAction):
    # Canonical identifiers
    type: str = "amazon_add_to_cart"
    product_name: Argument = Argument(
        value="laptop",
        description="Name or title of the product to add to shopping cart for purchase. Should match the product currently displayed on the product detail page. Examples: 'laptop' (current product), 'iPhone 15 Pro Max' (specific item), 'wireless charger' (product type), 'Nike Running Shoes' (brand and type). Adding to cart is the first step in the purchase process. The product must be on a product detail page, and all required options (size, color, quantity, etc.) should be selected before adding to cart. The item will be held in cart for later checkout."
    )

    # Schema payload
    descriptions: List[str] = [
        "Add ${{product_name}} to cart.",
        "Put this item in shopping cart.",
        "Add to cart.",
        "Buy ${{product_name}}.",
        "Add to basket."
    ]
    
    def __init__(self, product_name: str = "laptop", **kwargs) -> None:
        super().__init__(product_name=product_name, **kwargs)
        self.add_path(
            "amazon_add_to_cart",
            path=[
                SingleClickAction(thought="Click the Add to Cart button"),
                WaitAction(duration=2.0)
            ]
        )


@register("AmazonViewCart")
class AmazonViewCart(AmazonBaseAction):
    # Canonical identifiers
    type: str = "amazon_view_cart"

    # Schema payload
    descriptions: List[str] = [
        "View my cart.",
        "Check shopping cart.",
        "Show items in cart.",
        "Open cart page.",
        "View shopping cart."
    ]
    
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "amazon_view_cart",
            path=[
                SingleClickAction(thought="Click the cart button to view shopping cart"),
                WaitAction(duration=2.0)
            ]
        )


@register("AmazonRemoveFromCart")
class AmazonRemoveFromCart(AmazonBaseAction):
    # Canonical identifiers
    type: str = "amazon_remove_from_cart"
    product_name: Argument = Argument(
        value="laptop",
        description="Name or title of the product to remove from the shopping cart. Should match the product name as displayed in the cart page. Used for grounding to identify the specific item's Delete/Remove button in the cart. Examples: 'laptop' (product in cart), 'Apple AirPods Pro' (specific item), 'wireless mouse' (product type), 'Samsung Galaxy S23' (full name). Must be viewing the cart page to remove items. If multiple quantities of the same item exist, this will remove that product line entirely. Use this when you no longer want to purchase a particular item."
    )

    # Schema payload
    descriptions: List[str] = [
        "Remove ${{product_name}} from cart.",
        "Delete this item from cart.",
        "Take ${{product_name}} out of cart.",
        "Remove item from shopping cart.",
        "Clear ${{product_name}} from my cart."
    ]
    
    def __init__(self, product_name: str = "laptop", **kwargs) -> None:
        super().__init__(product_name=product_name, **kwargs)
        self.add_path(
            "amazon_remove_from_cart",
            path=[
                SingleClickAction(thought=f"Click the remove button for '{product_name}' in cart"),
                WaitAction(duration=1.0)
            ]
        )


@register("AmazonProceedToCheckout")
class AmazonProceedToCheckout(AmazonBaseAction):
    # Canonical identifiers
    type: str = "amazon_checkout"

    # Schema payload
    descriptions: List[str] = [
        "Proceed to checkout.",
        "Go to checkout.",
        "Start checkout process.",
        "Continue to payment.",
        "Check out now."
    ]
    
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "amazon_proceed_to_checkout",
            path=[
                SingleClickAction(thought="Click the Proceed to Checkout button"),
                WaitAction(duration=2.0)
            ]
        )


@register("AmazonSelectAddress")
class AmazonSelectAddress(AmazonBaseAction):
    # Canonical identifiers
    type: str = "amazon_select_address"
    address_label: Argument = Argument(
        value="Home",
        description="Label or identifier of the delivery address to select during checkout. Should match the address name/label as displayed in your Amazon account's address book. Common address labels: 'Home' (primary residence), 'Work' (office address), 'Mom\\'s House' (custom label), 'John Smith - 123 Main St' (recipient name and street), 'Default Address' (your default shipping address). Examples: 'Home' (select home address), 'Office' (work delivery), 'Parents House' (alternative location). The address must be previously saved in your Amazon account. This is used during the checkout process to specify where the order should be delivered."
    )

    # Schema payload
    descriptions: List[str] = [
        "Select address ${{address_label}}.",
        "Choose delivery to ${{address_label}}.",
        "Ship to ${{address_label}}.",
        "Select delivery address ${{address_label}}.",
        "Use ${{address_label}} for delivery."
    ]
    
    def __init__(self, address_label: str = "Home", **kwargs) -> None:
        super().__init__(address_label=address_label, **kwargs)
        self.add_path(
            "amazon_select_address",
            path=[
                SingleClickAction(thought=f"Select the '{address_label}' address option"),
                WaitAction(duration=1.0)
            ]
        )


@register("AmazonSelectPayment")
class AmazonSelectPayment(AmazonBaseAction):
    # Canonical identifiers
    type: str = "amazon_select_payment"
    payment_method: Argument = Argument(
        value="Credit Card",
        description="Payment method to use for completing the purchase during checkout. Should match the payment option name as displayed in your Amazon account's payment methods. Common payment methods: 'Credit Card' (credit/debit card), 'Visa ending in 1234' (specific card by last 4 digits), 'Mastercard' (card type), 'Amazon Gift Card' (gift card balance), 'Amazon Pay Balance' (account balance), 'PayPal' (PayPal account), 'Bank Account' (direct bank payment). Examples: 'Credit Card' (use saved card), 'Visa ending in 5678' (specific card), 'Gift Card Balance' (apply gift card). The payment method must be previously saved in your Amazon account or available as an option during checkout."
    )

    # Schema payload
    descriptions: List[str] = [
        "Pay with ${{payment_method}}.",
        "Select ${{payment_method}} as payment option.",
        "Use ${{payment_method}} for this order.",
        "Choose ${{payment_method}}.",
        "Set ${{payment_method}} for payment."
    ]

    def __init__(self, payment_method: str = "Credit Card", **kwargs) -> None:
        super().__init__(payment_method=payment_method, **kwargs)
        self.add_path(
            "amazon_select_payment",
            path=[
                SingleClickAction(thought=f"Select '{payment_method}' as payment method"),
                WaitAction(duration=1.0)
            ]
        )


@register("AmazonPlaceOrder")
class AmazonPlaceOrder(AmazonBaseAction):
    # Canonical identifiers
    type: str = "amazon_place_order"

    # Schema payload
    descriptions: List[str] = [
        "Place my order now.",
        "Confirm purchase.",
        "Order this item.",
        "Finish checkout.",
        "Complete my order."
    ]
    
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "amazon_place_order",
            path=[
                SingleClickAction(thought="Click the Place Order button to complete purchase"),
                WaitAction(duration=2.0)
            ]
        )


@register("AmazonOpenOrderPage")
class AmazonOpenOrderPage(AmazonBaseAction):
    # Canonical identifiers
    type: str = "amazon_open_order_page"
    
    # Schema payload
    descriptions: List[str] = [
        "Go to my orders page.",
        "Open order history.",
        "Show me my past orders.",
        "View my order list.",
        "Check my previous purchases."
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.add_path(
            "amazon_open_order_page",
            path=[
                SingleClickAction(thought="Click on Account and Lists menu"),
                WaitAction(duration=2.0),
                SingleClickAction(thought="Click on Your Orders button"),
                WaitAction(duration=2.0)
            ]
        )


@register("AmazonTrackOrder")
class AmazonTrackOrder(AmazonBaseAction):
    # Canonical identifiers
    type: str = "amazon_track_order"
    order_id: Argument = Argument(
        value="111-7777777-1234567",
        description="Amazon order identification number to track shipping status and delivery progress. Format: typically 17-18 characters in pattern XXX-XXXXXXX-XXXXXXX (three digit groups separated by hyphens). Examples: '111-7777777-1234567' (standard order ID), '123-4567890-9876543' (another order). Can be found in order confirmation emails, on the Orders page, or in your Amazon account under 'Your Orders'. Used to look up specific order details, tracking information, delivery estimates, and shipment status. Must be a valid order ID from your Amazon account history."
    )

    # Schema payload
    descriptions: List[str] = [
        "Track order ${{order_id}}.",
        "Check status of order ${{order_id}}.",
        "Show me the delivery status for ${{order_id}}.",
        "Track my package ${{order_id}}.",
        "Where is my order ${{order_id}}?"
    ]

    def __init__(self, order_id: str = "111-7777777-1234567", **kwargs) -> None:
        super().__init__(order_id=order_id, **kwargs)
        self.add_path(
            "amazon_track_order",
            path=[
                SingleClickAction(thought=f"Find and click on order {order_id} to track it"),
                WaitAction(duration=2.0)
            ]
        )


@register("AmazonCancelOrder")
class AmazonCancelOrder(AmazonBaseAction):
    # Canonical identifiers
    type: str = "amazon_cancel_order"
    order_id: Argument = Argument(
        value="111-7777777-1234567",
        description="Amazon order identification number for the order to cancel. Format: typically 17-18 characters in pattern XXX-XXXXXXX-XXXXXXX (three digit groups separated by hyphens). Examples: '111-7777777-1234567' (order to cancel), '123-4567890-9876543' (another order ID). The order must be in a cancellable state (not yet shipped/dispatched). Can be found in order confirmation emails or on Your Orders page. Note: Not all orders can be cancelled - Amazon only allows cancellation before the item ships. Digital orders and some third-party seller orders may have different cancellation policies. Used to stop an order before it's processed and shipped."
    )

    # Schema payload
    descriptions: List[str] = [
        "Cancel order ${{order_id}}.",
        "Stop the order ${{order_id}}.",
        "Cancel my purchase.",
        "Cancel this order.",
        "Stop my order."
    ]
    
    def __init__(self, order_id: str = "111-7777777-1234567", **kwargs) -> None:
        super().__init__(order_id=order_id, **kwargs)
        self.add_path(
            "amazon_cancel_order",
            path=[
                SingleClickAction(thought=f"Find order {order_id} and click cancel button"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Confirm cancellation"),
                WaitAction(duration=2.0)
            ]
        )


@register("AmazonReturnItem")
class AmazonReturnItem(AmazonBaseAction):
    # Canonical identifiers
    type: str = "amazon_return_item"
    order_id: Argument = Argument(
        value="111-7777777-1234567",
        description="Amazon order identification number for the item/order to return. Format: typically 17-18 characters in pattern XXX-XXXXXXX-XXXXXXX (three digit groups separated by hyphens). Examples: '111-7777777-1234567' (order to return), '123-4567890-9876543' (another order ID). The order must be eligible for return (usually within 30 days of delivery for most items, varies by product category). Can be found in order confirmation emails or on Your Orders page. Used to initiate the return process for unwanted, defective, or incorrect items. Return policies vary by product type, seller, and reason for return. Process includes selecting return reason, choosing return shipping method, and getting return authorization."
    )

    # Schema payload
    descriptions: List[str] = [
        "Return order ${{order_id}}.",
        "Start return process for ${{order_id}}.",
        "Request refund for order.",
        "Return this item.",
        "Return this order."
    ]
    
    def __init__(self, order_id: str = "111-7777777-1234567", **kwargs) -> None:
        super().__init__(order_id=order_id, **kwargs)
        self.add_path(
            "amazon_return_item",
            path=[
                SingleClickAction(thought=f"Find order {order_id} and click return button"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click return reason dropdown"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Select return reason"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Select return shipping option"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Select return method"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click confirm return button"),
                WaitAction(duration=2.0)
            ]
        )


@register("AmazonContactSeller")
class AmazonContactSeller(AmazonBaseAction):
    # Canonical identifiers
    type: str = "amazon_contact_seller"
    product_name: Argument = Argument(
        value="laptop",
        description="Name or title of the product for which you want to contact the seller. Should match the product currently being viewed on the product detail page. Used to identify which product's seller to contact. Examples: 'laptop' (current product), 'wireless headphones' (product type), 'Samsung Galaxy S23' (specific product), 'office chair' (item name). Used when you need to ask questions about the product, shipping, compatibility, or other product-specific inquiries before or after purchase. The product must be sold by a third-party seller (not Amazon directly) to have a 'Contact Seller' option available."
    )

    # Schema payload
    descriptions: List[str] = [
        "Message the seller of ${{product_name}}.",
        "Contact seller for ${{product_name}}.",
        "Send a question to seller of ${{product_name}}.",
        "Ask seller about ${{product_name}}.",
        "Reach out to seller of ${{product_name}}."
    ]

    def __init__(self, product_name: str = "laptop", **kwargs) -> None:
        super().__init__(product_name=product_name, **kwargs)
        self.add_path(
            "amazon_contact_seller",
            path=[
                SingleClickAction(thought="Click on the 'Sold by' link to go to seller page"),
                WaitAction(duration=2.0),
                SingleClickAction(thought="Click the Ask a question button"),
                WaitAction(duration=2.0)
            ]
        )


@register("AmazonLeaveReview")
class AmazonLeaveReview(AmazonBaseAction):
    # Canonical identifiers
    type: str = "amazon_leave_review"
    product_name: Argument = Argument(
        value="laptop",
        description="Name or title of the product to review. Should match a product you have previously purchased from Amazon. Used to identify which product in your order history to review. Examples: 'laptop' (purchased item), 'Apple AirPods Pro' (specific product), 'wireless mouse' (product type), 'Samsung TV' (item to review). You can only review products you have purchased through your Amazon account. The product should appear in your order history with a 'Write a product review' option available."
    )
    rating: Argument = Argument(
        value=5,
        description="Star rating for the product review. Must be an integer from 1 to 5. Rating meanings: 1 = Very dissatisfied/Poor quality (one star), 2 = Dissatisfied/Below expectations (two stars), 3 = Neutral/Average (three stars), 4 = Satisfied/Good quality (four stars), 5 = Very satisfied/Excellent (five stars). Examples: 5 (excellent product, highly recommend), 4 (good product with minor issues), 3 (okay product, meets basic expectations), 2 (disappointing, several issues), 1 (very poor quality, do not recommend). This rating helps other customers make purchasing decisions and provides feedback to sellers."
    )
    review_text: Argument = Argument(
        value="Great product! Highly recommend.",
        description="Written review content describing your experience with the product. Should be a detailed, helpful text explaining your thoughts, experiences, pros, cons, and recommendations. Can include information about quality, functionality, value, delivery, packaging, etc. Examples: 'Great product! Highly recommend.' (short positive), 'The quality exceeded my expectations. Works perfectly and arrived on time.' (detailed positive), 'Good value for money but the battery life could be better.' (balanced review), 'Unfortunately did not meet my needs. The size was smaller than expected.' (constructive negative). Amazon encourages detailed, honest reviews that help other customers. Minimum length requirements may apply. Avoid inappropriate content, personal information, or promotional material."
    )

    # Schema payload
    descriptions: List[str] = [
        "Leave a review.",
        "Rate this product.",
        "Write a review.",
        "Share my feedback.",
        "Submit my review."
    ]
    
    def __init__(self, product_name: str = "laptop", rating: int = 5, review_text: str = "Great product! Highly recommend.", **kwargs) -> None:
        super().__init__(product_name=product_name, rating=rating, review_text=review_text, **kwargs)
        self.add_path(
            "amazon_leave_review",
            path=[
                SingleClickAction(thought="Click write a customer review button"),
                WaitAction(duration=1.0),
                SingleClickAction(thought=f"Click {rating} stars for rating"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Click review text box"),
                WaitAction(duration=1.0),
                TypeAction(text=review_text, input_mode="copy_paste", thought=f"Type review: '{review_text}'"),
                WaitAction(duration=1.0),
                SingleClickAction(thought="Submit review"),
                WaitAction(duration=2.0)
            ]
        )

