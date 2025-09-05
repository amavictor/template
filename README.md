# TechMart E-commerce Platform

A modern Django-based e-commerce platform with advanced features including:

- **Multi-Factor Authentication (MFA)** with Microsoft Authenticator
- **Stripe Payment Integration** with hosted checkout
- **Product Management** with environmental sustainability tracking
- **Cart & Wishlist** functionality
- **API Access** with JWT token authentication
- **Admin Dashboard** with custom token generation

## 🚀 Quick Setup

### 1. Clone and Setup Environment

```bash
git clone <your-repo-url>
cd sprint-2-ecommerce
python -m venv bluewave_env
source bluewave_env/bin/activate  # On Windows: bluewave_env\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
cp .env.example .env
```

Then edit `.env` with your actual values:

```bash
# Required for basic functionality
SECRET_KEY=your-django-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Required for payments
STRIPE_PUBLISHABLE_KEY=pk_test_your_key_here
STRIPE_SECRET_KEY=sk_test_your_key_here
```

### 3. Database Setup

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 4. Run the Server

```bash
python manage.py runserver
```

Visit: `http://127.0.0.1:8000`

## 🔐 Multi-Factor Authentication

**All users must set up MFA using Microsoft Authenticator:**

1. **New User Signup**: Username/Password → **MFA Setup** → JWT Token
2. **Existing User Login**: Username/Password → **MFA Code** → JWT Token

### MFA Features:
- Microsoft Authenticator compatible (TOTP)
- QR code setup for easy configuration
- 8 emergency backup codes
- Mandatory for all users (except admin)

## 💳 Stripe Payment Integration

**Simple checkout flow:**

1. Add items to cart
2. Click "Proceed to Checkout"
3. Redirected to Stripe's secure checkout page
4. Payment processed
5. Order confirmation and tracking

### Test Cards:
- **Successful**: `4242 4242 4242 4242`
- **Expiry**: Any future date
- **CVC**: Any 3 digits

## 🛠 Admin Features

### Product Management:
- Full CRUD operations for products
- Environmental matrix tracking
- Stock management
- Image uploads

### API Token Generation:
- Custom token length (16-128 characters)
- Custom expiry dates
- Permission-based access
- JWT-based authentication

### Access Admin:
```
http://127.0.0.1:8000/admin/
```

## 🔌 API Usage

### Get API Token:
1. Login to admin dashboard
2. Go to "API Tokens"
3. Create new token with desired permissions
4. Copy the generated JWT token

### Use API Token:
```bash
curl -H "Authorization: Bearer your-jwt-token" \
     http://127.0.0.1:8000/api/products/
```

### API Endpoints:
- `GET /api/products/` - List products
- `GET /api/products/{id}/` - Product details
- `POST /api/cart/` - Add to cart
- `GET /api/cart/` - View cart
- `POST /api/wishlist/` - Add to wishlist

## 📁 Project Structure

```
sprint-2-ecommerce/
├── accounts/           # User management & MFA
├── products/           # Product catalog
├── cart/              # Shopping cart & wishlist
├── orders/            # Order management & payments
├── templates/         # HTML templates
├── static/           # CSS, JS, images
├── media/            # User uploads
└── bluewave_ecommerce/  # Project settings
```

## 🔧 Key Features

### Authentication & Security:
- Custom User model with username/password
- Microsoft Authenticator MFA (mandatory)
- JWT token authentication for API
- Session-based web authentication

### E-commerce Features:
- Product catalog with search
- Shopping cart with quantity management
- Wishlist functionality
- Stripe payment integration
- Order tracking and history

### Admin Features:
- Django admin customization
- API token management
- Product management
- User management (MFA status)

### API Features:
- REST API with DRF
- JWT authentication
- Swagger documentation
- Rate limiting and permissions

## 🚨 Security Notes

- `.env` file contains sensitive data - never commit to git
- MFA is mandatory for all regular users
- Admin accounts can bypass MFA for emergency access
- All API access requires valid JWT tokens
- Stripe handles payment data securely

## 🆘 Troubleshooting

### Common Issues:

1. **MFA not working**: Check device time synchronization
2. **Payment failing**: Verify Stripe keys in `.env`
3. **Import errors**: Ensure virtual environment is activated
4. **Database errors**: Run `python manage.py migrate`

### Support:
- Check Django logs in `django.log`
- Use debug toolbar in development
- Console logs for JavaScript issues

## 📝 Environment Variables

See `.env.example` for complete list of available environment variables.

**Required:**
- `SECRET_KEY`
- `STRIPE_PUBLISHABLE_KEY`
- `STRIPE_SECRET_KEY`

**Optional:**
- `DEBUG` (default: False)
- `ALLOWED_HOSTS` (default: localhost,127.0.0.1)
- `EMAIL_BACKEND` (for email notifications)
- `GOOGLE_OAUTH2_*` (if using Google OAuth)

---

**Built with Django 5.2.6, Python 3.13, and modern security practices.**
