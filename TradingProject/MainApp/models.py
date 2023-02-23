from django.db import models

# Create your models here.
class csvs(models.Model):
    file = models.FileField(upload_to='files/')
    timestamp = models.DateTimeField(auto_now_add=True)
    activated = models.BooleanField(default=False)

    def __str__(self):
        return str(self.file)

class candles(models.Model):
    csv = models.ForeignKey(csvs,on_delete=models.CASCADE)
    id = models.IntegerField(primary_key=True)
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    date = models.DateTimeField()

