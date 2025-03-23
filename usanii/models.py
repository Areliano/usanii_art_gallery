from django.db import models

# Create your models here.

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


class Exhibitions(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='exhibitions/')
    date = models.CharField(max_length=200, default='Saturday')
    description = models.TextField(max_length=1000, default='This is an exhibition')

    def __str__(self):
        return self.title

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



class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    date = models.DateField(null=True, blank=True)  # ✅ Ensure null & blank are allowed
    time = models.TimeField(null=True, blank=True)
    event = models.CharField(max_length=255, default="Unknown Event")
    is_approved = models.BooleanField(default=False)  # ✅ Ensure this exists

    def __str__(self):
        return self.name


class Reservation(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    event = models.CharField(max_length=255)
    is_approved = models.BooleanField(default=False)  # Status field

    def __str__(self):
        return self.name


class Moreartist(models.Model):
    name = models.CharField(max_length=500, default='text1')
    image = models.ImageField(upload_to='moreartist', default='moreartist.jpg')
    title = models.CharField(max_length=255, default='artists')
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name