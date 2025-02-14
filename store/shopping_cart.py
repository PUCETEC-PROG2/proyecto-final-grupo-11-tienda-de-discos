from decimal import Decimal

class ShoppingCart:
    def __init__(self, request):  
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart
    
    def save(self):
        self.session['cart'] = self.cart
        self.session.modified = True
    
    def add(self, product):
        product_id = str(product.id)
        
        if product_id not in self.cart:
            self.cart[product_id] = {
                'product_id': product.id,
                'name': product.name,
                'quantity': 1,
                'price': str(product.price),
                'picture': product.picture.url if product.picture else None,
            }
        else:
            current_quantity = self.cart[product_id]['quantity']
            if current_quantity < product.stock:
                self.cart[product_id]['quantity'] += 1
        
        self.save()
    
    def decrement(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            self.cart[product_id]['quantity'] -= 1
            if self.cart[product_id]['quantity'] < 1:
                self.remove(product)
            else:
                self.save()
    
    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()
    
    def clear(self):
        self.session['cart'] = {}
        self.session.modified = True
        
    def get_item_quantity(self, product_id):
        product_id = str(product_id)
        return self.cart.get(product_id, {}).get('quantity', 0)

    def get_subtotal(self):
        return sum(
            Decimal(item['price']) * item['quantity'] 
            for item in self.cart.values()
        )

    def get_total_with_tax(self):
        return sum(
            Decimal(item['price']) * item['quantity'] * Decimal('1.15')
            for item in self.cart.values()
        )
        
    def get_tax_amount(self):
        return self.get_total_with_tax() - self.get_subtotal()

