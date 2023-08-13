from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
#from django.contrib.gis.db import models as gis_models
#from django.contrib.gis.geos import Point
from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.


class BynryUserManager(BaseUserManager):
    def create_user(
        self,
        first_name,
        last_name,
        username,
        email,
        phone_number=None,
        password=None,
    ):
        if not email:
            raise ValueError("User must have an email address")

        if not username:
            raise ValueError("User must have an username")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, username, email, password=None):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user


class BynryUser(AbstractBaseUser):
    MANAGER = 1
    CUSTOMER = 2
    test = 3

    ROLE_CHOICE = ((MANAGER, "manager"), (CUSTOMER, "Customer"))
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=12, blank=True, null=True)
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICE, blank=True, null=True)

    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superadmin = models.BooleanField(default=False)

    # To set up customer default login field of the user use this property
    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    objects = BynryUserManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    def get_role(self):
        if self.role == 1:
            user_role = "Manager"
        else:
            user_role = "Customer"
        return user_role


class BynryUserProfile(models.Model):
    user = models.OneToOneField(
        BynryUser, on_delete=models.CASCADE, blank=True, null=True
    )
    profile_picture = models.ImageField(
        upload_to="users/profile_pictures", blank=True, null=True
    )
    cover_photo = models.ImageField(
        upload_to="users/cover_photos", blank=True, null=True
    )
    address = models.CharField(max_length=250, blank=True, null=True)
    country = models.CharField(max_length=20, blank=True, null=True)
    state = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=20, blank=True, null=True)
    pin_code = models.CharField(max_length=6, blank=True, null=True)
    latitude = models.CharField(max_length=20, blank=True, null=True)
    longitude = models.CharField(max_length=20, blank=True, null=True)
    # spatial reference id default
    create_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    # def full_address(self):
    #     return f"{self.address_line_1}, {self.address_line_2}"

    def __str__(self):
        return self.user.email

    def save(self, *args, **kwargs):
        if self.latitude and self.longitude:
            #self.location = Point(float(self.longitude), float(self.latitude))
            pass
        return super(BynryUserProfile, self).save(*args, **kwargs)
    
class FileUpload(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)


class ServiceRequests(models.Model):
    INSTALLATION = OPEN = LOW =0
    DELIVERY = ASSIGNED = MEDIUM =1
    SAFETY_INSPECTION = IN_PROGRESS = HIGH = 2
    MAINTENANCE = PENDING_CUSTOMER_RESPONSE = 3
    REPAIR = SCHEDULED = 4
    BILLING_ASSISTANCE = COMPLETED = 5
    ESCALATED = 6
    CLOSED = 7

    service_types = (
        (INSTALLATION, "Installation"),
        (DELIVERY, "Delivery"),
        (SAFETY_INSPECTION, "Safety Inspection"),
        (MAINTENANCE, "Maintenance"),
        (REPAIR, "Repairs"),
        (BILLING_ASSISTANCE, "Billing Assistance"),
    )

    status_types = (
        (OPEN, "Open"),
        (ASSIGNED, "Assigned"),
        (IN_PROGRESS, "In Progress"),
        (PENDING_CUSTOMER_RESPONSE, "Customer Response Pending"),
        (SCHEDULED, "Scheduled"),
        (COMPLETED, "Completed"),
        (ESCALATED, "Escalated"),
        (CLOSED, "Closed"),
    )
    PRIORITY_CHOICES = [
        (LOW, 'Low'),
        (MEDIUM, 'Medium'),
        (HIGH, 'High'),
    ]

    files = ArrayField(models.BigIntegerField(), null=True, blank=True)
    requested_by = models.ForeignKey(BynryUser, on_delete=models.CASCADE)
    service_type = models.PositiveSmallIntegerField(
        choices=service_types, blank=True, null=True
    )
    priority = models.PositiveSmallIntegerField(choices=PRIORITY_CHOICES, default=0)
    description = models.TextField()
    current_status = models.PositiveSmallIntegerField(
        choices=status_types, blank=True, null=True, default=0
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.requested_by
