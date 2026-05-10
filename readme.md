# Brandstore - Django Ecommerce Project
comprehensive ecommerce platform built with Django. It includes features like user authentication, product catalog management, a shopping cart, an order processing system, and a review and rating system.

### Main Project (`greatkart`)

This is the main Django project that orchestrates the different apps.

#### URLs (`greatkart/urls.py`)

-   `''` (root URL): Maps to `greatkart.views.home`, rendering the homepage.
-   `store/`: Includes all URL patterns from the `store` app.
-   `cart/`: Includes all URL patterns from the `carts` app.
-   `accounts/`: Includes all URL patterns from the `accounts` app.
-   `orders/`: Includes all URL patterns from the `orders` app.
-   `securelogin/`: The URL for the Django admin site.

#### Views (`greatkart/views.py`)

-   `home(request)`: Renders the main homepage (`home.html`). It fetches and displays available products, customer reviews, and testimonials.

---

### Accounts App (`accounts`)

Manages user authentication, profiles, and account-related activities.

#### URLs (`accounts/urls.py`)

-   `register/`: User registration page.
-   `login/`: User login page.
-   `logout/`: Logs the user out.
-   `dashboard/`: The user's personal dashboard.
-   `activate/<uidb64>/<token>/`: Activates a user account via an email link.
-   `forgotPassword/`: Page to request a password reset email.
-   `resetpassword_validate/<uidb64>/<token>/`: Validates the password reset link.
-   `resetPassword/`: Page to set a new password.
-   `my_orders/`: Displays a list of the user's past orders.
-   `edit_profile/`: Allows users to update their profile information.
-   `change_password/`: Allows users to change their current password.
-   `order_detail/<str:order_number>/`: Shows the detailed view of a specific order.

#### Views (`accounts/views.py`)

-   `register(request)`: Handles new user registration and sends an activation email.
-   `login(request)`: Authenticates the user. It also contains logic to merge a guest's shopping cart with the user's cart upon login.
-   `logout(request)`: Logs the user out and redirects to the login page.
-   `activate(request, ...)`: Handles the account activation link sent to the user's email.
-   `dashboard(request)`: Displays the user's dashboard, showing order history and profile information.
-   `forgotPassword(request)`: Manages the "forgot password" process by sending a reset link.
-   `resetpassword_validate(request, ...)`: Verifies the token from the password reset email.
-   `resetPassword(request)`: Allows the user to set a new password after validation.
-   `my_orders(request)`: Fetches and displays all orders belonging to the logged-in user.
-   `edit_profile(request)`: Handles the form for updating user details and profile picture.
-   `change_password(request)`: Handles the form for changing a user's password.
-   `order_detail(request, order_number)`: Displays a detailed breakdown of a single order, including products, pricing, and taxes.

---

### Carts App (`carts`)

Manages the shopping cart functionality.

#### URLs (`carts/urls.py`)

-   `''` (root of `/cart/`): Displays the main shopping cart page.
-   `add_cart/<int:product_id>/`: Adds a product to the cart.
-   `remove_cart/<int:product_id>/<int:cart_item_id>/`: Decreases the quantity of a specific item in the cart.
-   `remove_cart_item/<int:product_id>/<int:cart_item_id>/`: Completely removes an item from the cart.
-   `checkout/`: Displays the checkout page with the order summary.

#### Views (`carts/views.py`)

-   `_cart_id(request)`: A private helper function to get or create a session key for anonymous user carts.
-   `add_cart(request, product_id)`: Adds a selected product variation to the shopping cart. It handles logic for both authenticated and guest users.
-   `remove_cart(request, ...)`: Decrements the quantity of an item in the cart. If the quantity becomes zero, the item is removed.
-   `remove_cart_item(request, ...)`: Deletes an entire cart item row, regardless of quantity.
-   `cart(request)`: Renders the shopping cart page, calculating the subtotal, taxes, and grand total.
-   `checkout(request)`: Renders the checkout page, displaying the final order details before payment.

---

### Store App (`store`)

Handles the product catalog, product details, and customer reviews.

#### URLs (`store/urls.py`)

-   `''` (root of `/store/`): The main store page, listing all available products.
-   `category/<slug:category_slug>/`: Filters and displays products belonging to a specific category.
-   `category/<slug:category_slug>/<slug:product_slug>/`: Displays the detailed page for a single product.
-   `search/`: Handles product search queries.
-   `submit_review/<int:product_id>/`: Processes the submission of a product review.

#### Views (`store/views.py`)

-   `store(request, category_slug=None)`: Displays products. It can show all products or filter them by a given category slug. Includes pagination.
-   `product_detail(request, ...)`: Shows the detail page for a single product, including its image gallery, reviews, and available variations (color, size).
-   `search(request)`: Filters products based on a search keyword provided in the request.
-   `submit_review(request, product_id)`: Allows logged-in users to submit or update a review for a product they have purchased.

---

### Orders App (`orders`)

Manages the order creation and payment processing workflow.

#### URLs (`orders/urls.py`)

-   `place_order/`: Initiates the order placement process.
-   `payments/`: Handles the payment processing logic (e.g., integrating with a payment gateway).
-   `order_complete/`: Displays the order confirmation page after a successful payment.

#### Views (`orders/views.py`)

-   `payments(request)`: A backend endpoint that processes the payment information sent from the frontend (e.g., from PayPal). It creates a `Payment` record, updates the order status, moves cart items to the `OrderProduct` table, clears the cart, and sends a confirmation email.
-   `place_order(request)`: Handles the submission of the checkout form. It validates the form data, creates an `Order` record, and redirects the user to the payment page.
-   `order_complete(request)`: Renders the "Thank You" page after a successful order, showing the final order details and transaction ID.

---

### Category App (`category`)

This app defines the data model for product categories but does not have any views or URLs itself. The category logic is handled within the `store` app.

# Uncomment this from ./greatkart/wsgi.py in production server
#import sys
#sys.path.insert(0, '/var/www/html/Brandstore')
#sys.path.insert(0, '/var/www/html/Brandstore/venv')
#sys.path.insert(0, '/var/www/html/Brandstore/greatkart')


'NAME': BASE_DIR / 'db.sqlite3',
#'NAME': '/app/db/db.sqlite3', 
# Uncomment the above line and comment previous line in production server



# Uncomment this in ./greatkart/setting.py Production server
#EMAIL_HOST = '10.3.103.129'
#EMAIL_PORT = 25
#EMAIL_USE_TLS = False

# comment this in ./orders/views.py Production server
server.starttls()
server.login(sender_email, sender_password)

# Create db and media folders in the app directory before compiling

