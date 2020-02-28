from django.db import models

# Create your models here.
class Picture(models.Model):
    ## the auto incrimenting primary key
    id = models.AutoField(primary_key = True)

    ## the pic's name
    name = models.CharField(max_length = 15)

    ## grade the pic gets
    grade = models.CharField(max_length = 1)

    ## the weight of the food wasted
    weight = models.DecimalField(max_digits = 10, decimal_places = 3)

    ## when the pic was taken
    timestamp = models.DateTimeField()
