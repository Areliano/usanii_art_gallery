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


class Homepage(models.Model):
    heading = models.CharField(max_length=500, default='heading')
    description = models.TextField(max_length=3000, default='description')
    background_image1 = models.ImageField(upload_to='homepage', default='homepage.jpg')

    def __str__(self):
        return self.heading


class Artworks(models.Model):
    title = models.CharField(max_length=255, default='artists')
    name = models.CharField(max_length=500, default='text1')
    image = models.ImageField(upload_to='artistworks', default='artistsworks.jpg')
    price = models.CharField(max_length=255, default='5000')
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name


from django.db import models

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

    def is_full(self):
        return self.current_attendees >= self.max_capacity

    def available_spots(self):
        return self.max_capacity - self.current_attendees

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Exhibition"
        verbose_name_plural = "Exhibitions"



class Booking(models.Model):
    exhibition = models.ForeignKey(Exhibition, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    booking_date = models.DateTimeField(auto_now_add=True)
    is_confirmed = models.BooleanField(default=True)

    class Meta:
        unique_together = ('email', 'exhibition')  # Prevent duplicate bookings

    def __str__(self):
        return f"{self.name} - {self.exhibition.title}"


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