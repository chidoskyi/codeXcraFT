from .models import AppInfo

def slick(request):
        info = AppInfo.objects.get(pk=1)
        
        context = {
            'info':info, 
        }
        
        
        return context