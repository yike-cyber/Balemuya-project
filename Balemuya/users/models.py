from django.db import models
import uuid
from datetime import timedelta
from django.utils import timezone
from cloudinary.models import CloudinaryField
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager,PermissionsMixin
from decimal import Decimal
from django.core.exceptions import ValidationError

# Address Model
class Address(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    country = models.CharField(max_length=100, default='Ethiopia')
    region = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    latitude = models.DecimalField(
        max_digits=10, decimal_places=8, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=11, decimal_places=8, null=True, blank=True
    )

    def __str__(self):
        return f"{self.country}, {self.region}, {self.city}"

    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not password:
            raise ValueError('The Password field must be set')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'admin')
        extra_fields.setdefault('is_active', True)

        return self.create_user(email, password, **extra_fields)

# User Types
ENTITY_TYPE_CHOICES = [
    ('organization', 'Organization'),
    ('individual', 'Individual'),
    ('admin', 'Admin'),
]
USER_TYPE_CHOICES = [
    ('customer', 'Customer'),
    ('professional', 'Professional'),
    ('admin', 'Admin'),
]

class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=200, unique=True)
    username = models.CharField(max_length = 100,null=True,blank=True)
    phone_number = models.CharField(max_length=30,null=True,blank=True )
    profile_image = CloudinaryField('image', null=True, blank=True, folder='Profile/profile_images')
    address = models.ForeignKey('Address', on_delete=models.SET_NULL, related_name='users', null=True, blank=True)
    gender = models.CharField(max_length=50,choices=[('male','Male'),('female','Female')],null=True,blank=True)
    first_name = models.CharField(max_length=100,null=True,blank=True)
    last_name = models.CharField(max_length=100,null=True,blank=True)
    org_name = models.CharField(max_length=100,null=True,blank=True)
    bio = models.TextField(blank=True, null=True)
     
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='customer')
    entity_type = models.CharField(max_length=30, choices=ENTITY_TYPE_CHOICES, default='individual')
    
    telegram_chat_id = models.CharField(max_length=255,unique=True, null=True, blank=True)


    is_active = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    
    date_joined = models.DateTimeField(default=timezone.now)

    last_login = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False) 

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number']

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    
    def get_full_name(self):
        if self.entity_type == 'individual':
            return f"{self.first_name} {self.last_name}" if self.first_name and self.last_name else self.username
        elif self.entity_type == 'organization':
            return self.org_name if self.org_name else self.username
        return self.username
    
    
    def clean(self):
        if not isinstance(self.id, uuid.UUID):
            raise ValidationError({'id': ('Invalid UUID format.')})

    def save(self, *args, **kwargs):
        self.clean() 
        super().save(*args, **kwargs)

###############  Base User Mixin ###########################
class BaseUserMixin(models.Model):
    description = models.TextField(blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    tx_number = models.CharField(max_length=100,null=True,blank=True)
    number_of_employees = models.IntegerField(default=0)
    report_count = models.IntegerField(default=0)


    class Meta:
        abstract = True
        
    
############### customer  Model ###########################
class Customer(BaseUserMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name='customer')
    number_of_services_booked = models.PositiveIntegerField(default=0)    
    
    def __str__(self):
        return self.user.email

    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
    
    def __str__(self):
        return self.user.email
    
    
    
class Professional(BaseUserMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name='professional')
    skills = models.ManyToManyField('Skill', blank=True, related_name='professionals')
    categories = models.ManyToManyField(
        'common.Category', blank=True, related_name='professionals'
    )
    years_of_experience = models.PositiveIntegerField(default=0)
    
    is_verified = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    num_of_request = models.IntegerField(default=0)


    kebele_id_front_image = CloudinaryField(
        'image', null=True, blank=True, folder='Professional/kebele_id_images/front_images'
    )
    kebele_id_back_image = CloudinaryField(
        'image', null=True, blank=True, folder='Professional/kebele_id_images/back_images'
    )

    def __str__(self):
        return self.user.email

    class Meta:
        verbose_name = 'Professional'
        verbose_name_plural = 'Professionals'

    
################## Feedback  model #####################
class Feedback(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')
    message = models.TextField()
    rating = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.created_at}"

    class Meta:
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedbacks'

###################  Permission Model   ##########################
class Permission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Permission'
        verbose_name_plural = 'Permissions'


##########################  Admin Model #############################
class Admin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin')
    full_name = models.CharField(max_length=30,null=True,blank=True)
    gender = models.CharField(max_length=30, choices=[('male', 'Male'), ('female', 'Female')],null=True)
    permissions = models.ManyToManyField(Permission, blank=True, related_name='admins')
    admin_level = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.email} - Admin Level {self.admin_level}"

    class Meta:
        verbose_name = 'Admin'
        verbose_name_plural = 'Admins'

    def has_perm(self, perm):
        return self.permissions.filter(name=perm).exists()


############# Admin Action Log ########################
class AdminLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE, related_name='logs')
    action = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.admin.user.email} - {self.action}"

    class Meta:
        verbose_name = 'Admin Log'
        verbose_name_plural = 'Admin Logs'


############### Skill Model for Professionals ##########################
class Skill(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Skill'
        verbose_name_plural = 'Skills'


##################3 Education Model for Professionals ###################
class Education(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    professional = models.ForeignKey(
        'Professional', on_delete=models.CASCADE, related_name='educations'
    )
    school = models.CharField(max_length=100)
    degree = models.CharField(max_length=100, blank=True, null=True)
    field_of_study = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.professional.user.user_type != 'professional':
            raise ValueError("Only professionals can have education records.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.school} - {self.degree or 'N/A'}"

    class Meta:
        verbose_name = 'Education'
        verbose_name_plural = 'Educations'
        ordering = ['-created_at']

class Portfolio(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    professional = models.ForeignKey(
        'Professional', on_delete=models.CASCADE, related_name='portfolios'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = CloudinaryField('image', null=True, blank=True, folder='PortfolioImages/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.professional.user.user_type != 'professional':
            raise ValueError("Only professionals can create portfolios.")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Portfolio'
        verbose_name_plural = 'Portfolios'
        ordering = ['-created_at']



# Certificate Model for Professionals
class Certificate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    professional = models.ForeignKey(
        'Professional', on_delete=models.CASCADE, related_name='certificates' 
    )
    image = CloudinaryField(
        'certificate_image', null=True, blank=True, folder='Certificates'
    )
    name = models.CharField(max_length=100, blank=True, null=True)  # Changed to CharField
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.professional.user.user_type != 'professional':
            raise ValueError("Only professionals can create certificates.")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name or 'Unnamed Certificate'

    class Meta:
        verbose_name = 'Certificate'
        verbose_name_plural = 'Certificates'
        ordering = ['-created_at']

# Subscription Plan
class SubscriptionPlan(models.Model):
    PLAN_CHOICES = [
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('diamond', 'Diamond'),
    ]
    
    REQUEST_COINS= {
         'silver':50,
        'gold': 100,
        'diamond': 150
    }
    
    MONTHLY_COSTS = {
        'silver': Decimal('100.00'),
        'gold': Decimal('200.00'),
        'diamond': Decimal('300.00'),
    }
    
    DURATION_CHOICES = [
        (1, '1 Month'),
        (3, '3 Months'),
        (6, '6 Months'),
        (12, '1 Year'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    professional = models.ForeignKey('Professional', on_delete=models.CASCADE, related_name='subscription_plan',default=None) 
    plan_type = models.CharField(max_length=20, choices=PLAN_CHOICES)
    duration = models.IntegerField(choices=DURATION_CHOICES)
    cost = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(editable=False)

    def save(self, *args, **kwargs):
        try:
            if self.plan_type in self.MONTHLY_COSTS and self.duration:
                monthly_cost = self.MONTHLY_COSTS[self.plan_type]
                self.cost = monthly_cost * self.duration
                self.end_date = self.start_date + timedelta(days=self.duration * 30)
            else:
                raise ValueError("Missing plan_type or duration for cost calculation.")
        except Exception as e:
            raise ValueError("Invalid plan_type or duration.")

        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.end_date if self.end_date else False

    def __str__(self):
        return f"{self.professional.email} - {self.plan_type} - {self.duration} Month(s)"

    class Meta:
        verbose_name = 'Subscription Plan'
        verbose_name_plural = 'Subscription Plans'



class Bank(models.Model):
    """
    Represents a bank with its name and code.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    code = models.PositiveIntegerField(unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Bank"
        verbose_name_plural = "Banks"

def load_initial_banks():
    """
    Loads initial bank data into the Bank model.  This can be called from a data migration.
    """
    BANK_CHOICES = [
        (130, 'Abay Bank'),
        (772, 'Addis International Bank'),
        (207, 'Ahadu Bank'),
        (656, 'Awash Bank'),
        (347, 'Bank of Abyssinia'),
        (571, 'Berhan Bank'),
        (128, 'CBEBirr'),
        (946, 'Commercial Bank of Ethiopia (CBE)'),
        (893, 'Coopay-Ebirr'),
        (880, 'Dashen Bank'),
        (1, 'Enat Bank'),
        (301, 'Global Bank Ethiopia'),
        (534, 'Hibret Bank'),
        (612, 'Hijra Bank'),
        (202, 'Lion Bank'),
        (325, 'Nib International Bank'),
        (896, 'Oromia Bank'),
        (287, 'Siinqee Bank'),
        (465, 'Tsehay Bank'),
        (614, 'ZamZam Bank'),
        (451, 'Zemen Bank'),
    ]

    for code, name in BANK_CHOICES:
        Bank.objects.get_or_create(code=code, defaults={'name': name})


class BankAccount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    professional = models.OneToOneField('Professional', on_delete=models.CASCADE, related_name='bank_account')
    account_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=20)
    bank = models.ForeignKey('Bank', on_delete=models.PROTECT, related_name='bank_accounts', null=True, blank=True)  
    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.account_name}"

    class Meta:
        verbose_name = 'Bank Account'
        verbose_name_plural = 'Bank Accounts'
        
# Payment Model for Services
class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='service_payments', null=True)  
    professional = models.ForeignKey('Professional', on_delete=models.CASCADE, related_name='received_payments',null=True) 
    booking = models.ForeignKey('services.ServiceBooking', on_delete=models.CASCADE,null=True,blank=True)
    service_request = models.ForeignKey('services.ServiceRequest', on_delete=models.CASCADE,null=True,blank=True)
    payment_type = models.CharField(max_length=30,choices=[('job_post','Job Post'),('direct_request','Direct Request')],null=True,blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2,default=0) 
    payment_date = models.DateTimeField(default=timezone.now)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=50, default='chapa', null=True, blank=True)
    transaction_id = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"Payment {self.transaction_id} from {self.customer.user.email} to {self.professional.user.email} - Amount: {self.amount}"

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'


# Subscription Payment Model
class SubscriptionPayment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subscription_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, related_name='subscription_payments')
    professional = models.ForeignKey('Professional', on_delete=models.CASCADE, related_name='subscription_payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    payment_date = models.DateTimeField(default=timezone.now)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=50, default='chapa', null=True, blank=True)
    transaction_id = models.CharField(max_length=100, unique=True)

    def save(self, *args, **kwargs):
        self.amount = self.subscription_plan.cost
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Subscription Payment {self.transaction_id} for {self.professional.user.email} - Amount: {self.amount}"

    class Meta:
        verbose_name = 'Subscription Payment'
        verbose_name_plural = 'Subscription Payments'
        
        
        
class WithdrawalTransaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    professional = models.ForeignKey('Professional', on_delete=models.CASCADE, related_name='withdrawal_transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tx_ref = models.CharField(max_length=100, unique=True) 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Withdrawal of {self.amount} by {self.professional.user.email} - {self.status}"

    class Meta:
        verbose_name = 'Withdrawal Transaction'
        verbose_name_plural = 'Withdrawal Transactions'
        
class VerificationRequest(models.Model):
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    professional = models.OneToOneField('Professional', on_delete=models.CASCADE,null=False, related_name='verification_requests')
    verified_by = models.ForeignKey('Admin', on_delete=models.SET_NULL, null=True, blank=True, related_name='verifications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    class Meta:
         unique_together = ('professional', 'status')
         
         
    def save(self, *args, **kwargs):
        if self.status in ['approved', 'rejected'] and not self.verified_by:
            raise ValueError("An admin must verify the request before approving or rejecting.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Verification Request for {self.professional} staus {self.status}"
    

class Favorite(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    professional = models.ForeignKey(Professional, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f'{self.user.username} favorites {self.professional.user.username}'
    
