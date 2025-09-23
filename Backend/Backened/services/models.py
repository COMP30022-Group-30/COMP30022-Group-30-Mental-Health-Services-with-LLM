from django.db import models

# Create your models here.
class organisation(models.Model):
    organisation_key = models.UUIDField(primary_key=True, editable=False, auto_now_add=True)
    organisation_name = models.CharField(max_length=100)

    def __str__(self):
        return f"Organisation {self.organisation_name}"

class service(models.Model):
    service_key = models.UUIDField(primary_key=True, editable=False, auto_now_add=True)
    organisation_key = models.ForeignKey(organisation, on_delete=models.CASCADE)
    service_name = models.CharField(max_length=100)

    def __str__(self):
        return f" Service {self.service_name}"
    
class campus(models.Model):
    campus_key = models.UUIDField(primary_key=True, editable=False, auto_now_add=True)
    organisation_key = models.ForeignKey(organisation, on_delete=models.CASCADE)
    campus_name = models.CharField(max_length=100)

    def __str__(self):
        return f" Campus {self.campus_name}"
    
class service_campus(models.Model):
    service_campus_key = models.UUIDField(primary_key=True, editable=False, auto_now_add=True)
    service_key = models.ForeignKey(service, on_delete=models.CASCADE)
    campus_key = models.ForeignKey(campus, on_delete=models.CASCADE)
    email = models.EmailField(max_length=50, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    website = models.URLField(max_length=100, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    expectesd_wait_time = models.CharField(max_length=20, null=True, blank=True)
    op_hours_24_7 = models.BooleanField(default=False, null=True, blank=True)
    op_hours_standard = models.BooleanField(default=False, null=True, blank=True)
    op_hours_extended = models.BooleanField(default=False, null=True, blank=True)
    op_hours_extended_details = models.TextField(null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    suburb = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    postcode = models.CharField(max_length=10, null=True, blank=True)
    eligibility_and_discription = models.TextField(null=True, blank=True)

    def __str__(self):
        return f" Service Campus {self.service_campus_key}"
    
class service_type(models.Model):
    SERVICE_TYPE = [
        ('Mental Health promotion'),
        ('Mental Illness prevention'),
        ('Primary and Specialised clinical ambulatory mental health care services'),
        ('Specialised mental health community support services'),
        ('Specialised bed-based mental health care services'),
        ('Medication and prodeures'),
        ]
    
    service_type_key = models.UUIDField(primary_key=True, editable=False, auto_now_add=True)
    service_campus_key = models.ForeignKey(service_campus, on_delete=models.CASCADE)
    service_type_num = models.IntegerField(choices=[1,2,3,4,5,6], null=True, blank=True)
    service_type = models.CharField(max_length=100, null=True, blank=True, choices=SERVICE_TYPE)

    def __str__(self):
        return f" Service Type {self.service_type_key}"

class target_population(models.Model):
    TARGET_POPULATION = [  
        ('AOD'),
        ('Aboriginal and Torres Strait Islander'),
        ('Adult'),
        ('Children'),
        ('Culturally and Linguistically Diverse'),
        ('Families'),
        ('Homeless'),
        ('Hospital'),
        ('LGBTQIA+'),
        ('Older Adults'),
        ('Specialised Services'),
        ('Young People'),
        ]
    
    target_population_key = models.UUIDField(primary_key=True, editable=False, auto_now_add=True)
    service_campus_key = models.ForeignKey(service_campus, on_delete=models.CASCADE)
    target_population = models.CharField(choices=TARGET_POPULATION)

    def __str__(self):
        return f" Target Population {self.target_population_key}"

class service_region(models.Model):
        service_campus_key = models.ForeignKey(service_campus, on_delete=models.CASCADE, null=True, blank=True, auto_now_add=True)
        region_key = models.ForeignKey('region', on_delete=models.CASCADE, null=True, blank=True)
    
        def __str__(self):
            return f" Service Region {self.service_campus_key} - {self.region_key}"

class level_of_care(models.Model):
    LEVEL_OF_CARE = [
        ('Self management'),
        ('Low intensity'),
        ('Moderate intensity'),
        ('High intensity'),
        ('Specialist'),
        ]
    
    level_of_care_key = models.UUIDField(primary_key=True, editable=False, auto_now_add=True)
    service_campus_key = models.ForeignKey(service_campus, on_delete=models.CASCADE)
    level_of_care_num = models.IntegerField(choices=[1,2,3,4,5], null=True, blank=True)
    level_of_care = models.CharField(choices=LEVEL_OF_CARE, null=True, blank=True)

    def __str__(self):
        return f" Level of Care {self.level_of_care_key}"
    
class cost(models.Model):
    COST_OPTIONS = [
        ('Free'),
        ('N/A'),
        ('Paid'),
        ]

    cost_key = models.UUIDField(primary_key=True, editable=False, auto_now_add=True)
    service_campus_key = models.ForeignKey(service_campus, on_delete=models.CASCADE)
    cost = models.CharField(choices=COST_OPTIONS)

    def __str__(self):
        return f" Cost {self.cost_key}"

class referral_pathway(models.Model):
    REFERRAL_PATHWAY = [
        ('Doctor/GP referral'),
        ('Free call'),
        ('General booking'),
        ('Varies depending on service'),
        ]
    
    referral_pathway_key = models.UUIDField(primary_key=True, editable=False, auto_now_add=True)
    service_campus_key = models.ForeignKey(service_campus, on_delete=models.CASCADE)
    referral_pathway = models.TextField(choices=REFERRAL_PATHWAY)

    def __str__(self):
        return f" Referral Pathway {self.referral_pathway_key}"

class workforce_type(models.Model):
    WORKFORCE_TYPE = [
        ('Medical'),
        ('Peer worker'),
        ('Tertiary qualified'),
        ('Vocationally qualified'),
        ]

    workforce_type_key = models.UUIDField(primary_key=True, editable=False, auto_now_add=True)
    service_campus_key = models.ForeignKey(service_campus, on_delete=models.CASCADE)
    workforce_type = models.CharField(choices=WORKFORCE_TYPE)

    def __str__(self):
        return f" Workforce Type {self.workforce_type_key}"
    
class delivery_method(models.Model):
    DELIVERY_METHOD = [
        ('In person'),
        ('Online'),
        ('Outreach'),
        ]
    
    delivery_method_key = models.UUIDField(primary_key=True, editable=False, auto_now_add=True)
    service_campus_key = models.ForeignKey(service_campus, on_delete=models.CASCADE)
    delivery_method = models.CharField(choices=DELIVERY_METHOD)

    def __str__(self):
        return f" Delivery Method {self.delivery_method_key}"
    
class region(models.Model):
    region_key = models.UUIDField(primary_key=True, editable=False, auto_now_add=True)
    region_name = models.CharField(max_length=100)

    def __str__(self):
        return f" Region {self.region_name}"
    
class postcode(models.Model):
    postcode_key = models.UUIDField(primary_key=True, editable=False, auto_now_add=True)
    region_key = models.ForeignKey(region, on_delete=models.CASCADE)
    postcode = models.CharField(max_length=10)

    def __str__(self):
        return f" Postcode {self.postcode_key}"