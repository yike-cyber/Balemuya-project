from rest_framework import serializers
import re
import dns.resolver
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _
from .models import User, Address, Permission, AdminProfile, AdminLog, CustomerProfile, Skill, ProfessionalProfile, Education, Portfolio, Certificate

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'
        
class UserSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many = True)
    
    class Meta:
        model = User
        fields = ['id', 'first_name', 'middle_name', 'last_name', 'gender', 
                  'email', 'phone_number', 'profile_image', 'kebele_id_image', 
                  'user_type', 'bio', 'last_login', 'created_at', 'addresses']
        
        extra_kwargs = {
            'password':{'write_only':True}
        }
        
        def validate_email(self,value):
            
            try:
                validate_email(value)
            except ValidationError:
                raise serializers.ValidationError(_("Invalid  email format."))
            
            domain = value.split('@')[-1]
            try:
                dns.resolver.resolve(domain, 'MX')
            except(dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
                raise serializers.ValidationError(_("Email domain does not exist."))
            
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError("User with this Email already exists")
            return value

        def validate_phone_number(self,value):
            
            if not re.match(r'^\+?1?\d{9,15}$', value):
                  raise serializers.ValidationError(_("Phone number must be in a valid format."))
            
            
            
            if User.objects.filter(phone_number=value).exists():
                raise serializers.ValidationError("User with this phone number already exists")
            return value
        
        def validate_password(self,value):
            if len(value)<8:
                raise serializers.ValidationError(_("Password must be at least 8 characters long."))
            
            return value
        
        def create(self, validated_data):
            addresses_data = validated_data.pop('addresses', [])
            user = User.objects.create(**validated_data)
            user.set_password(validated_data['password'])
            user.save()
            
            # Create or reuse addresses
            for address_data in addresses_data:
                address, created = Address.objects.get_or_create(
                    user=user,
                    country=address_data['country'],
                    region=address_data['region'],
                    woreda=address_data['woreda'],
                    city=address_data.get('city', ''),  # Default to empty string
                    kebele=address_data['kebele'],
                    street=address_data['street'],
                    latitude=address_data['latitude'],
                    longitude=address_data['longitude']
                )

                if address_data.get('is_current'):
                    Address.objects.filter(user=user, is_current=True).update(is_current=False)
                    address.is_current = True
                    address.save()

            return user

            
        def update(self, instance, validated_data):
            addresses_data = validated_data.pop('addresses', None)

            # Update user fields
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            # Update addresses if provided
            if addresses_data is not None:
                for address_data in addresses_data:
                    address, created = Address.objects.get_or_create(
                        user=instance,
                        country=address_data['country'],
                        region=address_data['region'],
                        woreda=address_data['woreda'],
                        city=address_data.get('city', ''),
                        kebele=address_data['kebele'],
                        street=address_data['street'],
                        latitude=address_data['latitude'],
                        longitude=address_data['longitude']
                    )
                    
                    # Optionally set the current address flag
                    if address_data.get('is_current'):
                        Address.objects.filter(user=instance, is_current=True).update(is_current=False)
                        address.is_current = True
                        address.save()

            return instance
                
            
                

        
class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = '__all__'
    
    def create(self,validated_data):
        skill_data = validated_data
        if Skill.objects.filter(name=skill_data['name']).exists():
            pass
        else:
            skill = Skill.objects.create(name = skill_data['name'])
            
        return skill



class PermissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Permission
        fields = '__all__'
        
class AdminProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer() 
    permissions = PermissionSerializer(many=True)

    class Meta:
        model = AdminProfile
        fields = ['user', 'permissions', 'admin_level']
        
class AdminLogSerializer(serializers.ModelSerializer):
    admin = AdminProfileSerializer()

    class Meta:
        model = AdminLog
        fields = ['admin', 'action', 'timestamp']
        
        
class CustomerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = CustomerProfile
        fields = ['user', 'rating', 'total_interactions']


class EducationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Education
        fields = [ 'school', 'degree', 'field_of_study', 'location', 'document_url', 'start_date', 'end_date', 'honors', 'is_current_student']

# Portfolio Serializer
class PortfolioSerializer(serializers.ModelSerializer):

    class Meta:
        model = Portfolio
        fields = [ 'title', 'description', 'image', 'video_url', 'created_at', 'updated_at']

# Certificate Serializer
class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = [ 'name', 'issued_by', 'document_url', 'date_issued', 'expiration_date', 'certificate_type', 'is_renewable', 'renewal_period']
        
class ProfessionalProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    skills = SkillSerializer(many=True)
    educations = EducationSerializer(many=True)
    portfolios = PortfolioSerializer(many=True)
    certificates = CertificateSerializer(many=True)

    class Meta:
        model = ProfessionalProfile
        fields = ['user', 'skills', 'educations', 'portfolios', 'certificates',
                  'is_verified', 'business_logo', 'business_card', 
                  'rating', 'years_of_experience', 'portfolio_url', 'availability']

    def create(self, validated_data):
        user_data = validated_data.pop('user', {})
        educations_data = validated_data.pop('educations', [])
        certifications_data = validated_data.pop('certificates', [])
        portfolios_data = validated_data.pop('portfolios', [])
        skills_data = validated_data.pop('skills', [])
        business_card = validated_data.pop('business_card', None)
        business_logo = validated_data.pop('business_logo', None)

        user_serializer = UserSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)  # Validate user data
        user = user_serializer.save()  

        professional_profile = ProfessionalProfile.objects.create(
            user=user,
            business_card=business_card,
            business_logo=business_logo,
            **validated_data
        )

        for skill_data in skills_data:
            skill_serializer = SkillSerializer(data=skill_data)
            skill_serializer.is_valid(raise_exception=True)  # Validate skill data
            skill_serializer.save(profile=professional_profile)  # Create Skill instance

        for education_data in educations_data:
            education_serializer = EducationSerializer(data=education_data)
            education_serializer.is_valid(raise_exception=True)  # Validate education data
            education_serializer.save(profile=professional_profile)  # Create Education instance

        for portfolio_data in portfolios_data:
            portfolio_serializer = PortfolioSerializer(data=portfolio_data)
            portfolio_serializer.is_valid(raise_exception=True)  # Validate portfolio data
            portfolio_serializer.save(profile=professional_profile)  # Create Portfolio instance

        for certification_data in certifications_data:
            certificate_serializer = CertificateSerializer(data=certification_data)
            certificate_serializer.is_valid(raise_exception=True)  # Validate certificate data
            certificate_serializer.save(profile=professional_profile)  # Create Certificate instance

        return professional_profile


