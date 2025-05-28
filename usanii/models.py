from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Aboutpage(models.Model):
    heading = models.CharField(max_length=500, default='heading')
    welcome = models.CharField(max_length=500, default='welcome')
    description = models.TextField(max_length=3000, default='description')
    special = models.CharField(max_length=500, default='special')
    cool = models.TextField(max_length=3000, default='description')

    def __str__(self):
        return self.heading


class Artists(models.Model):
    name = models.CharField(max_length=500, default='text1')
    date = models.CharField(max_length=500, default='text2')
    text1 = models.TextField(max_length=500, default='text3')
    image = models.ImageField(upload_to='artists', default='artists.jpg')

    def __str__(self):
        return self.name

    @property
    def artwork_count(self):
        return self.artworks.count()  # This will use the reverse relation

class Homepage(models.Model):
    heading = models.CharField(max_length=500, default='heading')
    description = models.TextField(max_length=3000, default='description')
    background_image1 = models.ImageField(upload_to='homepage', default='homepage.jpg')

    def __str__(self):
        return self.heading


# models.py
from django.contrib.auth.models import User

class Artworks(models.Model):
    artist = models.ForeignKey(
        Artists,
        on_delete=models.CASCADE,
        related_name='artworks',
        null=True,
        blank=True
    )
    title = models.CharField(max_length=255, default='artists')
    name = models.CharField(max_length=500, default='text1')
    category = models.CharField(max_length=100, blank=True, null=True)  # Added for category reports
    image = models.ImageField(upload_to='artistworks', default='artistsworks.jpg')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=5000)  # Changed from CharField
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Exhibition(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='exhibitions/')
    date = models.CharField(max_length=200, default='Saturday')
    description = models.TextField(max_length=1000, default='This is an exhibition')
    start_time = models.TimeField(
        help_text="Format: HH:MM (24-hour format), e.g. 18:00 for 6 PM"
    )
    end_time = models.TimeField(
        help_text="Format: HH:MM (24-hour format), e.g. 21:00 for 9 PM"
    )
    max_capacity = models.PositiveIntegerField(default=50)
    current_attendees = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)  # Added for better reporting
    booking_date = models.DateTimeField(default=timezone.now)

    def is_full(self):
        return self.current_attendees >= self.max_capacity

    def available_spots(self):
        return self.max_capacity - self.current_attendees

    def booking_count(self):
        """Returns total number of bookings for this exhibition"""
        return self.booking_set.count()

    def attendance_percentage(self):
        """Returns percentage of seats filled"""
        if self.max_capacity == 0:
            return 0
        return round((self.current_attendees / self.max_capacity) * 100, 2)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Exhibition"
        verbose_name_plural = "Exhibitions"
        ordering = ['-created_at']  # Newest exhibitions first

class Booking(models.Model):
    exhibition = models.ForeignKey(
        Exhibition,
        on_delete=models.CASCADE,
        related_name='bookings'  # Added for easier querying
    )
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    booking_date = models.DateTimeField(auto_now_add=True)
    is_confirmed = models.BooleanField(default=True)
    attended = models.BooleanField(default=False)  # Track if they actually attended
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # Added for customer reports

    class Meta:
        unique_together = ('email', 'exhibition')  # Prevent duplicate bookings
        ordering = ['-booking_date']  # Newest bookings first
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"

    def __str__(self):
        return f"{self.name} - {self.exhibition.title} (Confirmed: {self.is_confirmed})"

    def save(self, *args, **kwargs):
        """Update exhibition attendees when booking is confirmed"""
        if self.is_confirmed and not self.attended:
            self.exhibition.current_attendees += 1
            self.exhibition.save()
        super().save(*args, **kwargs)

class Contact(models.Model):
    name = models.CharField(max_length=500, default='text1')
    address = models.CharField(max_length=500, default='text1')
    phone = models.CharField(max_length=500, default='text1')
    email = models.CharField(max_length=500, default='text1')
    website = models.CharField(max_length=500, default='text1')

    def __str__(self):
        return self.name


class Footer(models.Model):
    heading = models.CharField(max_length=500, default='text1')
    about = models.CharField(max_length=500, default='text1')
    twitter = models.CharField(max_length=500, blank=False, null=False)
    facebook = models.CharField(max_length=500, blank=False, null=False)
    instagram = models.CharField(max_length=500, blank=False, null=False)
    open_days = models.CharField(max_length=500, default='text1')
    newsletter = models.CharField(max_length=500, default='text1')
    image1 = models.ImageField(upload_to='footer', default='testimony.jpg')
    image2 = models.ImageField(upload_to='footer', default='testimony.jpg')
    image3 = models.ImageField(upload_to='footer', default='testimony.jpg')
    image4 = models.ImageField(upload_to='footer', default='testimony.jpg')
    image5 = models.ImageField(upload_to='footer', default='testimony.jpg')
    image6 = models.ImageField(upload_to='footer', default='testimony.jpg')

    def __str__(self):
        return self.heading


class Moreartist(models.Model):
    name = models.CharField(max_length=500, default='text1')
    image = models.ImageField(upload_to='moreartist', default='moreartist.jpg')
    title = models.CharField(max_length=255, default='artists')
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name

# Your existing models.py content (ensure all necessary imports are at the top)
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

    def __str__(self):
        if self.user:
            return f"Cart for {self.user.username}"
        return f"Cart for session {self.session_key or 'N/A'}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    artwork = models.ForeignKey('Artworks', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_price(self):
        return float(self.artwork.price) * float(self.quantity)

    def __str__(self):
        return f"{self.quantity} x {self.artwork.title} (Kshs. {self.total_price})"


# Your existing Payment and Order models
class Payment(models.Model):
    phone_number = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    receipt_number = models.CharField(max_length=50, default='SIM' + str(timezone.now().timestamp())[:8])
    status = models.CharField(max_length=20, default='pending', choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')]) # Added choices for clarity
    transaction_date = models.DateTimeField(auto_now_add=True)
    reference = models.CharField(max_length=50, unique=True)
    delivery_address = models.TextField(blank=True, null=True)
    customer_email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"Payment #{self.reference} - Kshs. {self.amount} ({self.status})"

class Order(models.Model):
    order_number = models.CharField(max_length=50, unique=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True)
    is_delivered = models.BooleanField(default=False)

    @property
    def get_items(self):
        return self.items.all() # Relation to OrderItem

    def __str__(self):
        return f"Order #{self.order_number}"

# NEW: OrderItem model to store individual items within an order
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    artwork = models.ForeignKey('Artworks', on_delete=models.PROTECT) # PROTECT prevents deletion of artwork if part of an order
    quantity = models.PositiveIntegerField(default=1)
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2) # Store price at time of purchase

    @property
    def total_price(self):
        return self.quantity * self.price_at_purchase

    def __str__(self):
        return f"{self.quantity} x {self.artwork.title} for Order {self.order.order_number}"