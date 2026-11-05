class LandingSection(models.Model):
    name = 'hero'
    text = models.TextField()
    price = models.DecimalField()
    editable_by_superadmin = True

# Views CRUD /api/superadmin/landing/

