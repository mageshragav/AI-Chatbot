"""
Database schema documentation for ERP chatbot.
Auto-generated from database schema with enhanced descriptions.
This helps the chatbot understand the database structure and provide accurate responses.
"""

SCHEMA_DOCUMENTATION = {
    
    'Product': {
        'table': 'products_product',
        'app': 'products',
        'description': 'Main product catalog containing jewelry items with weight, metal type, and pricing details',
        'common_fields': ['id', 'name', 'product_id', 'weight', 'gold_weight', 'qty', 'metal_type', 'category', 'price'],
        'foreign_keys': {
            'base_product_id': 'products_product (self-reference for variants)',
            'category_id': 'catalog_category',
            'collection_id': 'catalog_collection',
            'diamond_quality_id': 'manufacturing_diamondquality',
            'gender_id': 'catalog_gender',
            'hallmark_id': 'manufacturing_hallmark',
            'manufacturing_id': 'manufacturing_manufacturing',
            'metal_type_id': 'manufacturing_metaltype',
            'project_id': 'projects_project',
            'sub_category_id': 'catalog_subcategory',
            'sub_collection_id': 'catalog_subcollection',
            'unit_id': 'projects_unit',
            'default_variant_id': 'products_productvariant',
        },
        'reverse_relations': {
            'order_lines': 'order_management_orderline.tej_product_id',
            'product_variants': 'products_productvariant.product_id',
            'diamond_details': 'diamond_stone_details.product_id',
            'stone_details': 'manufacturing_stonedetails.product_id',
            'customer_views': 'customers_productcustomer.product_id',
            'making_charges': 'customers_productmakingchargepercustomer.product_id',
            'fast_moving_zones': 'products_fastmovingzone.product_id',
            'popular_design_zones': 'products_populardesignzone.product_id',
            'product_surveys': 'products_productsurvey.product_id',
        },
        'sample_queries': [
            'how many products do we have',
            'show me ring products',
            'list gold products',
            'products with zero stock',
            'most popular product',
            'best selling product',
        ],
        'keywords': ['product', 'inventory', 'stock', 'catalog', 'jewelry', 'item', 'sku', 'popular', 'best']
    },
    
    'ProductVariant': {
        'table': 'products_productvariant',
        'app': 'products',
        'description': 'Product variants with specific carat, color, size combinations',
        'relationships': {
            'product': 'Product (via product_id)',
            'variant': 'Variant (via variant_id - carat/color/size combo)',
        },
        'keywords': ['variant', 'sku', 'variation', 'option']
    },
    
    'Category': {
        'table': 'catalog_category',
        'app': 'catalog',
        'description': 'Product categories (Ring, Necklace, Bracelet, Earring, Pendant, etc.)',
        'common_fields': ['id', 'category_name', 'description'],
        'sample_queries': [
            'list categories',
            'categories with product count',
            'show ring category',
        ],
        'keywords': ['category', 'type', 'classification']
    },
    
    'SubCategory': {
        'table': 'catalog_subcategory',
        'app': 'catalog',
        'description': 'Product subcategories for finer classification',
        'keywords': ['subcategory', 'sub-category']
    },
    
    'Collection': {
        'table': 'catalog_collection',
        'app': 'catalog',
        'description': 'Product collections/series (e.g., Bridal, Festival, Designer)',
        'sample_queries': ['show collections', 'products in bridal collection'],
        'keywords': ['collection', 'series', 'line']
    },
    
    'SubCollection': {
        'table': 'catalog_subcollection',
        'app': 'catalog',
        'description': 'Sub-collections within main collections',
        'keywords': ['subcollection', 'sub-collection']
    },
    
    'Gender': {
        'table': 'catalog_gender',
        'app': 'catalog',
        'description': 'Gender classification (Ladies, Gents, Kids, Unisex)',
        'keywords': ['gender', 'ladies', 'gents', 'men', 'women', 'kids']
    },
    
    'FastMovingZone': {
        'table': 'products_fastmovingzone',
        'app': 'products',
        'description': 'Fast-moving/high-demand product zones',
        'keywords': ['fast moving', 'popular', 'high demand', 'trending']
    },
    
    'PopularDesignZone': {
        'table': 'products_populardesignzone',
        'app': 'products',
        'description': 'Popular design categories and trending styles',
        'keywords': ['popular design', 'trending', 'popular', 'hot design']
    },

    
    'Order': {
        'table': 'order_management_order',
        'app': 'order_management',
        'description': 'Customer orders - main order header with customer and status information',
        'common_fields': ['id', 'tab_order_no', 'customer', 'user', 'status', 'created_at', 'hallmarked'],
        'foreign_keys': {
            'cart_id': 'django_content_type (GenericForeignKey)',
            'cart_object_id': 'Used with cart_id for GenericForeignKey to Cart/CustomOrderCart',
            'customer_id': 'customers_customer',
            'user_id': 'users_user (who placed the order)',
            'user_preference_id': 'users_userpreference',
            'created_by_id': 'users_user',
            'updated_by_id': 'users_user',
            'approved_by_id': 'customers_customer',
            'requested_by_id': 'customers_customer',
        },
        'reverse_relations': {
            'order_splits': 'order_management_ordersplit.order_id',
            'reorder_history': 'order_management_reorderhistory.order_id',
            'reorder_tracks': 'order_management_reordertrack.order_id',
            'cart_reorders': 'cart_cart.reordered_from_order_id',
            'custom_cart_reorders': 'custom_order_customordercart.reordered_from_order_id',
        },
        'sample_queries': [
            'how many orders this month',
            'recent orders',
            'orders by customer',
            'pending orders',
            'which customer has most orders',
        ],
        'keywords': ['order', 'sale', 'purchase', 'transaction', 'booking']
    },
    
    'OrderSplit': {
        'table': 'order_management_ordersplit',
        'app': 'order_management',
        'description': 'Order splits by carat and color for manufacturing/ERP integration',
        'common_fields': ['id', 'order', 'color', 'carat', 'tej_order_id', 'total_weight', 'total_quantity'],
        'relationships': {
            'order': 'Order (via order_id)',
            'color': 'Color (via color_id)',
            'carat': 'Carat (via carat_id)',
            'order_lines': 'OrderLine (reverse: multiple lines per split)',
        },
        'keywords': ['order split', 'split', 'batch']
    },
    
    'OrderLine': {
        'table': 'order_management_orderline',
        'app': 'order_management',
        'description': 'Individual line items within orders - products ordered with quantities',
        'common_fields': ['id', 'order_split', 'tej_product', 'total_quantity', 'total_weight', 'delivery_date', 'mc_percentage'],
        'foreign_keys': {
            'order_split_id': 'order_management_ordersplit',
            'tej_product_id': 'products_product (DIRECT FK - USE THIS FOR PRODUCT QUERIES)',
            'custom_product_id': 'custom_order_customproduct',
            'product_id': 'django_content_type (GenericForeignKey)',
            'product_object_id': 'Used with product_id for GenericForeignKey',
            'cart_variant_id': 'django_content_type (GenericForeignKey)',
            'cart_variant_object_id': 'Used with cart_variant_id for GenericForeignKey',
            'project_warehouse_id': 'products_projectwarehouse',
            'created_by_id': 'users_user',
            'updated_by_id': 'users_user',
        },
        'reverse_relations': {
            'cart_variants_reorder': 'cart_cartproductvariants.order_variant_from_order_id',
            'custom_cart_variants_reorder': 'custom_order_customordercartproductvariants.order_variant_from_order_id',
            'reorder_history': 'order_management_reorderhistory.order_line_id',
            'reorder_tracks': 'order_management_reordertrack.order_line_id',
        },
        'important_note': '⚠️ CRITICAL: Always use tej_product_id for product queries, NOT the generic product_id field!',
        'sample_queries': [
            'which product ordered most',
            'most popular product',
            'products sold last month',
            'order items',
        ],
        'keywords': ['order line', 'line item', 'ordered product', 'sale item']
    },
    
    'ReorderHistory': {
        'table': 'order_management_reorderhistory',
        'app': 'order_management',
        'description': 'History of reordered items and repeat purchases',
        'keywords': ['reorder', 'repeat order', 're-order']
    },
    
    'ReorderTrack': {
        'table': 'order_management_reordertrack',
        'app': 'order_management',
        'description': 'Tracking reorder requests and fulfillment',
        'keywords': ['reorder track', 'reorder tracking']
    },
    
    
    'Customer': {
        'table': 'customers_customer',
        'app': 'customers',
        'description': 'Customer master data - dealers, retailers, end customers',
        'common_fields': ['id', 'customer_id', 'name', 'email', 'phone', 'customer_role', 'is_active'],
        'foreign_keys': {
            'dealer_id': 'customers_customer (self-reference for dealer hierarchy)',
            'zone_id': 'projects_zone',
            'created_by_id': 'users_user',
            'updated_by_id': 'users_user',
        },
        'reverse_relations': {
            'orders': 'order_management_order.customer_id',
            'user_preferences': 'users_userpreference.customer_id',
            'users': 'users_user.customer_id',
            'invoices': 'invoice_invoice.customer_id',
            'carts': 'cart_cart.customer_id',
            'custom_carts': 'custom_order_customordercart.customer_id',
            'custom_products': 'custom_order_customproduct.customer_id',
            'product_views': 'customers_productcustomer.customer_id',
            'making_charges': 'customers_productmakingchargepercustomer.customer_id',
            'reorder_history': 'order_management_reorderhistory.customer_id',
            'reorder_tracks': 'order_management_reordertrack.customer_id',
            'sub_dealers': 'customers_customer.dealer_id (reverse self-reference)',
            'order_approvals': 'order_management_order.approved_by_id',
            'order_requests': 'order_management_order.requested_by_id',
        },
        'sample_queries': [
            'show customers',
            'top customers',
            'customer with most orders',
            'list all dealers',
            'active customers',
        ],
        'keywords': ['customer', 'client', 'buyer', 'dealer', 'retailer', 'account']
    },
    
    'ProductCustomer': {
        'table': 'customers_productcustomer',
        'app': 'customers',
        'description': 'Customer-specific product views and interactions',
        'keywords': ['customer product', 'product view', 'customer interaction']
    },
    
    'ProductMakingChargePerCustomer': {
        'table': 'customers_productmakingchargepercustomer',
        'app': 'customers',
        'description': 'Custom making charges defined per customer',
        'keywords': ['making charge', 'custom pricing', 'customer pricing']
    },

    
    'User': {
        'table': 'users_user',
        'app': 'users',
        'description': 'System users - sales reps, admin staff, dealers',
        'common_fields': ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'user_type'],
        'foreign_keys': {
            'customer_id': 'customers_customer',
            'created_by_id': 'users_user (self-reference)',
            'updated_by_id': 'users_user (self-reference)',
        },
        'reverse_relations': {
            'orders_placed': 'order_management_order.user_id',
            'carts': 'cart_cart.user_id',
            'custom_carts': 'custom_order_customordercart.user_id',
            'user_preferences': 'users_userpreference.user_id',
            'user_addon': 'users_useraddon.user_id',
            'product_surveys': 'products_productsurvey.user_id',
            'reorder_history': 'order_management_reorderhistory.user_id',
            'reorder_tracks': 'order_management_reordertrack.user_id',
            'created_users': 'users_user.created_by_id (self-reference)',
            'updated_users': 'users_user.updated_by_id (self-reference)',
            'created_orders': 'order_management_order.created_by_id',
            'created_products': 'custom_order_customproduct.created_by_id',
            'audio_uploads': 'cart_cartvariantaudioannotation.uploaded_by_id',
        },
        'sample_queries': [
            'which user has most orders',
            'top users',
            'active users',
            'list all users',
        ],
        'keywords': ['user', 'staff', 'employee', 'sales rep', 'admin']
    },
    
    'UserPreference': {
        'table': 'users_userpreference',
        'app': 'users',
        'description': 'User preferences and default settings',
        'keywords': ['preference', 'settings', 'defaults']
    },
    
    'UserAddon': {
        'table': 'users_useraddon',
        'app': 'users',
        'description': 'Additional user properties and operational zones',
        'keywords': ['addon', 'user addon', 'operational zone']
    },
    
    
    'Carat': {
        'table': 'manufacturing_carat',
        'app': 'manufacturing',
        'description': 'Gold carat options (14K, 18K, 22K, 24K)',
        'sample_queries': ['list carats', 'show 18K products'],
        'keywords': ['carat', 'purity', '14k', '18k', '22k', '24k', 'karat']
    },
    
    'Color': {
        'table': 'manufacturing_color',
        'app': 'manufacturing',
        'description': 'Gold/metal color options (Yellow, White, Rose)',
        'sample_queries': ['show yellow gold products', 'white gold items'],
        'keywords': ['color', 'gold color', 'yellow', 'white', 'rose', 'metal color']
    },
    
    'MetalType': {
        'table': 'manufacturing_metaltype',
        'app': 'manufacturing',
        'description': 'Metal types (Gold, Silver, Platinum)',
        'keywords': ['metal type', 'gold', 'silver', 'platinum', 'metal']
    },
    
    'Hallmark': {
        'table': 'manufacturing_hallmark',
        'app': 'manufacturing',
        'description': 'Hallmark certification types',
        'keywords': ['hallmark', 'certification', 'bis']
    },
    
    'Manufacturing': {
        'table': 'manufacturing_manufacturing',
        'app': 'manufacturing',
        'description': 'Manufacturing methods (Casting, Handmade, etc.)',
        'keywords': ['manufacturing', 'production method', 'casting', 'handmade']
    },
    
    'Size': {
        'table': 'manufacturing_size',
        'app': 'manufacturing',
        'description': 'Product sizes (ring sizes, bangle sizes, etc.)',
        'keywords': ['size', 'ring size', 'bangle size']
    },
    
    'Style': {
        'table': 'manufacturing_style',
        'app': 'manufacturing',
        'description': 'Design styles and patterns',
        'keywords': ['style', 'design', 'pattern']
    },
    
    'DiamondQuality': {
        'table': 'manufacturing_diamondquality',
        'app': 'manufacturing',
        'description': 'Diamond quality grades (VS, SI, VVS, etc.)',
        'keywords': ['diamond quality', 'clarity', 'grade', 'vs', 'si', 'vvs']
    },
    
    'DiamondColor': {
        'table': 'manufacturing_diamondcolor',
        'app': 'manufacturing',
        'description': 'Diamond color grades (D, E, F, etc.)',
        'keywords': ['diamond color', 'color grade']
    },
    
    'DiamondSize': {
        'table': 'manufacturing_diamondsize',
        'app': 'manufacturing',
        'description': 'Diamond sizes and dimensions',
        'keywords': ['diamond size', 'carat size']
    },
    
    'DiamondSieveCode': {
        'table': 'manufacturing_diamondsievecode',
        'app': 'manufacturing',
        'description': 'Diamond sieve codes for sorting',
        'keywords': ['sieve code', 'diamond sorting']
    },
    
    'DiamondStyle': {
        'table': 'manufacturing_diamondstyle',
        'app': 'manufacturing',
        'description': 'Diamond cutting styles (Round, Princess, Emerald, etc.)',
        'keywords': ['diamond style', 'cut', 'round', 'princess', 'emerald cut']
    },
    
    'DiamondUnit': {
        'table': 'manufacturing_diamondunit',
        'app': 'manufacturing',
        'description': 'Units for diamond measurement',
        'keywords': ['diamond unit', 'measurement']
    },
    
    'StoneType': {
        'table': 'manufacturing_stonetype',
        'app': 'manufacturing',
        'description': 'Types of gemstones (Ruby, Emerald, Sapphire, etc.)',
        'keywords': ['stone type', 'gemstone', 'ruby', 'emerald', 'sapphire']
    },
    
    'StoneDetails': {
        'table': 'manufacturing_stonedetails',
        'app': 'manufacturing',
        'description': 'Gemstone details for products',
        'keywords': ['stone details', 'gemstone info']
    },
    
    'DiamondStoneDetails': {
        'table': 'diamond_stone_details',
        'app': 'products',
        'description': 'Diamond stone details for products',
        'keywords': ['diamond details', 'diamond info']
    },
    
    'MakingCharge': {
        'table': 'manufacturing_makingcharge',
        'app': 'manufacturing',
        'description': 'Making charges for different product types',
        'keywords': ['making charge', 'labor cost', 'manufacturing cost']
    },
    
    'DesignBank': {
        'table': 'manufacturing_designbank',
        'app': 'manufacturing',
        'description': 'Design repository and design codes',
        'keywords': ['design bank', 'design code', 'design repository']
    },
    
    'DesignBatch': {
        'table': 'manufacturing_designbatch',
        'app': 'manufacturing',
        'description': 'Design batches for production',
        'keywords': ['design batch', 'production batch']
    },
    
    
    'Project': {
        'table': 'projects_project',
        'app': 'projects',
        'description': 'Projects and client-specific collections',
        'common_fields': ['id', 'project_name', 'description', 'is_active'],
        'sample_queries': [
            'list projects',
            'top selling projects',
            'best projects',
        ],
        'keywords': ['project', 'client project', 'collection']
    },
    
    'Unit': {
        'table': 'projects_unit',
        'app': 'projects',
        'description': 'Measurement units (grams, pieces, sets)',
        'keywords': ['unit', 'measurement', 'uom']
    },
    
    'Zone': {
        'table': 'projects_zone',
        'app': 'projects',
        'description': 'Geographic zones and operational areas',
        'keywords': ['zone', 'area', 'region', 'territory']
    },
    
    'OrderSplitByProject': {
        'table': 'order_management_ordersplitbyproject',
        'app': 'order_management',
        'description': 'Order splits organized by project',
        'keywords': ['order split', 'project split']
    },
    
    
    'Cart': {
        'table': 'cart_cart',
        'app': 'cart',
        'description': 'Shopping carts for regular products',
        'keywords': ['cart', 'shopping cart', 'basket']
    },
    
    'CartProductVariants': {
        'table': 'cart_cartproductvariants',
        'app': 'cart',
        'description': 'Product variants added to cart',
        'keywords': ['cart item', 'cart product']
    },
    
    'CartVariantAudioAnnotation': {
        'table': 'cart_cartvariantaudioannotation',
        'app': 'cart',
        'description': 'Audio annotations/notes for cart items',
        'keywords': ['audio note', 'cart note', 'voice annotation']
    },
    
    'CustomOrderCart': {
        'table': 'custom_order_customordercart',
        'app': 'custom_order',
        'description': 'Shopping carts for custom/made-to-order products',
        'keywords': ['custom cart', 'custom order', 'bespoke']
    },
    
    'CustomProduct': {
        'table': 'custom_order_customproduct',
        'app': 'custom_order',
        'description': 'Custom designed products (made-to-order)',
        'keywords': ['custom product', 'bespoke', 'made to order', 'customized']
    },
    
    'CustomOrderVariant': {
        'table': 'custom_order_customordervariant',
        'app': 'custom_order',
        'description': 'Variants for custom products',
        'keywords': ['custom variant', 'custom option']
    },
    
    
    'Invoice': {
        'table': 'invoice_invoice',
        'app': 'invoice',
        'description': 'Customer invoices and billing documents',
        'sample_queries': ['show invoices', 'invoices this month', 'customer invoices'],
        'keywords': ['invoice', 'bill', 'billing', 'receipt']
    },
    
    'InvoiceProducts': {
        'table': 'invoice_invoiceproducts',
        'app': 'invoice',
        'description': 'Products listed in invoices',
        'keywords': ['invoice item', 'invoice product', 'billing item']
    },
    
    'InwardMovement': {
        'table': 'invoice_inwardmovement',
        'app': 'invoice',
        'description': 'Inventory inward movements (stock received)',
        'keywords': ['inward', 'receipt', 'stock in', 'receiving']
    },
    
    'OutwardMovement': {
        'table': 'invoice_outwardmovement',
        'app': 'invoice',
        'description': 'Inventory outward movements (stock issued)',
        'keywords': ['outward', 'issue', 'stock out', 'dispatch']
    },
    
    
    'ProductSurvey': {
        'table': 'products_productsurvey',
        'app': 'products',
        'description': 'Product surveys and customer feedback',
        'keywords': ['survey', 'feedback', 'review', 'rating']
    },
}


def get_model_by_keyword(keyword: str) -> list:
    """Find models matching a keyword."""
    keyword_lower = keyword.lower()
    results = []
    
    for model_name, info in SCHEMA_DOCUMENTATION.items():
        keywords = info.get('keywords', [])
        if keyword_lower in [k.lower() for k in keywords]:
            results.append((model_name, info))
        elif keyword_lower in model_name.lower():
            results.append((model_name, info))
        elif keyword_lower in info.get('description', '').lower():
            results.append((model_name, info))
    
    return results


def get_model_info(model_name: str) -> dict:
    """Get information about a specific model."""
    return SCHEMA_DOCUMENTATION.get(model_name, {})


def get_all_models() -> list:
    """Get list of all documented models."""
    return list(SCHEMA_DOCUMENTATION.keys())


def search_sample_queries(query_text: str) -> list:
    """Find models with matching sample queries."""
    query_lower = query_text.lower()
    results = []
    
    for model_name, info in SCHEMA_DOCUMENTATION.items():
        sample_queries = info.get('sample_queries', [])
        for sample in sample_queries:
            if query_lower in sample.lower():
                results.append((model_name, info, sample))
                break
    
    return results
