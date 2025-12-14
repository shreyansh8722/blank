from django.db import models
from users.models import *
from cog_static_app.models import *
from django.utils.text import slugify 
from PIL import Image
from io import BytesIO
from django.core.files import File

class Newsletter(models.Model):

    email = models.EmailField(blank=True, null=True)
    
    def __str__(self):
        return str(self.email)

    class Meta:
        verbose_name_plural = "Subscribers"

class Testimonials(models.Model):

    name = models.CharField(max_length=200,blank=True,null=True)
    image = models.ImageField(blank=False,null=True,default=None)
    designation = models.CharField(max_length=50,blank=True,null=True)
    rating = models.DecimalField(max_digits=1, decimal_places=0, null=True, blank=True,verbose_name='Rating (1-5)')
    testimonial = models.TextField(blank=True, null=True)
    sequences= models.IntegerField(null=True)

    def __str__(self):
        return self.name
        
    def save(self, *args, **kwargs):
        new_image = self.reduce_image_size(self.image)
        self.image = new_image
        super().save(*args, **kwargs)
        
    def reduce_image_size(self, image):
        img = Image.open(image)
        thumb_io = BytesIO()
        img.save(thumb_io, 'jpeg', quality=50)
        new_image = File(thumb_io, name=image.name)
        return new_image

    class Meta:
        verbose_name_plural = "Testimonials"
type = (
    ('Teacher', 'Teacher'),
    ('School', 'School'),
    )
class Faq(models.Model):

    question = models.TextField(blank=True,null=True)
    answer = models.TextField(blank=True,null=True)
    type = models.CharField(max_length=55,choices=type, default=None, blank=True,null=True)

    def __str__(self):
        return self.question

    class Meta:
        verbose_name_plural = "FAQ's"

class Inquiry(models.Model):

    name = models.CharField(max_length=200,null=True, blank=True)
    email = models.EmailField(blank=True, null=True)
    mobile_no = models.CharField(max_length=15, null=True, blank=True)
    message = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Inquiry"

class Banner(models.Model):

    image = models.ImageField(blank=False,null=True)
    title = models.CharField(max_length=200,null=True, blank=True)
    info = models.CharField(max_length=550,null=True, blank=True)

    def __str__(self):
        return self.title
        
    def save(self, *args, **kwargs):
        new_image = self.reduce_image_size(self.image)
        self.image = new_image
        super().save(*args, **kwargs)
        
    def reduce_image_size(self, image):
        img = Image.open(image)
        thumb_io = BytesIO()
        img.save(thumb_io, 'jpeg', quality=50)
        new_image = File(thumb_io, name=image.name)
        return new_image

    class Meta:
        verbose_name_plural = "Banner"

class Team(models.Model):

    name = models.CharField(max_length=200,null=True, blank=True)
    image = models.ImageField(blank=False, null=True)
    designation = models.CharField(max_length=50,null=True, blank=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        new_image = self.reduce_image_size(self.image)
        self.image = new_image
        super().save(*args, **kwargs)

    def reduce_image_size(self, image):
        img = Image.open(image)
        thumb_io = BytesIO()
        img.save(thumb_io, 'jpeg', quality=50)
        new_image = File(thumb_io, name=image.name)
        return new_image

    class Meta:
        verbose_name_plural = "Team"

class Blogs(models.Model):

    title = models.CharField(max_length=200,null=True,blank=True)
    slug = models.SlugField(max_length=1024,null=True,blank=True)
    image = models.ImageField(blank=False, null=True)
    blog = models.TextField(blank=True, null=True)
    date = models.DateField(null=True,blank=True)
    author = models.CharField(max_length=50,null=True,blank=True)
    tag = models.CharField(max_length=50,null=True,blank=True)
    location = models.CharField(max_length=100,null=True,blank=True)

    class Meta:
        verbose_name_plural = "Blogs"
        
    def save(self, *args, **kwargs):
        new_image = self.reduce_image_size(self.image)
        self.image = new_image
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)
        
    def reduce_image_size(self, image):
        img = Image.open(image)
        thumb_io = BytesIO()
        img.save(thumb_io, 'jpeg', quality=50)
        new_image = File(thumb_io, name=image.name)
        return new_image

    def __str__(self):
        return self.title

class Review(models.Model):

    name = models.CharField(max_length=200,null=True,blank=True)
    email = models.EmailField(blank=True, null=True)
    image = models.ImageField(blank=False, null=True)
    rating = models.IntegerField(blank=True, null=True)                                                                                                                                                                                                                                                                              
    review = models.TextField(blank=True, null=True)
    date = models.DateField(auto_now=True,null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.name
        
    def save(self, *args, **kwargs):
        new_image = self.reduce_image_size(self.image)
        self.image = new_image
        super().save(*args, **kwargs)
        
    def reduce_image_size(self, image):
        img = Image.open(image)
        thumb_io = BytesIO()
        img.save(thumb_io, 'jpeg', quality=50)
        new_image = File(thumb_io, name=image.name)
        return new_image

    class Meta:
        verbose_name_plural = "Reviews"

class TermsAndConditions(models.Model):

    title = models.CharField(max_length=200, default=None, blank=True)
    terms = models.TextField(blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Terms And Conditions"

class PrivacyPolicy(models.Model):

    title = models.CharField(max_length=200, default=None, blank=True)
    policy = models.TextField(blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Privacy Policy"        

class RefundCancellationPolicy(models.Model):

    title = models.CharField(max_length=200, default=None, blank=True)
    policy = models.TextField(blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Refund/Cancellation Policy"        

