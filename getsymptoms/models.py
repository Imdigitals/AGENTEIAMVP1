from django.db import models

class Cita(models.Model):
    fecha = models.DateField()
    hora = models.TimeField()
    especialidad = models.CharField(max_length=100)
    contacto = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cita en {self.especialidad} para {self.fecha} a las {self.hora}"
