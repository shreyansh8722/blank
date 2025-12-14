from .models import DailyVisitorCount
from django.utils import timezone
import socket
class VisitorCounttMiddleware:
    def __init__(self, get_response):
       
        self.get_response=get_response
    def __call__(self, request):
        user_id=None
       
        if request.user.is_authenticated:
            user_id=request.user.id
        ip_address=self.get_client_ip(request)
        today=timezone.now().date()
        try:
            if user_id and ip_address:
                try:
                    daily_count=DailyVisitorCount.objects.get(date=today, user_id=user_id, ip_address=ip_address)
                except Exception:
                    daily_count=DailyVisitorCount.objects.get(date=today, ip_address=None, user_id=None)
                    daily_count.user_id=user_id
                    daily_count.save()

            else:
                daily_count=DailyVisitorCount.objects.get(date=today, ip_address=None, user_id=None)
        except DailyVisitorCount.DoesNotExist:
            if user_id and ip_address:
                daily_count=DailyVisitorCount(date=today, user_id=user_id, ip_address=ip_address)
            else:
                daily_count=DailyVisitorCount(date=today, ip_address=ip_address)
        daily_count.count +=1
      
        daily_count.save()
        response=self.get_response(request)
        return response
            

    def get_client_ip(self, request):
        x_forwarded_for=request.META.get('HTTP_X_FORWARDED_FOR')
        return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

    

    # def get_ip_address():
    #     try:
    #         # Create a socket object to get the local machine's IP address
    #         s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
    #         # Connect to an external server (in this case, Google's public DNS server)
    #         s.connect(('8.8.8.8', 80))
            
    #         # Get the local IP address
    #         ip_address = s.getsockname()[0]
            
    #     except Exception as e:
    #         print(f"Error: {e}")
    #         ip_address = None
            
    #     finally:
    #         # Close the socket
    #         s.close()

    #     return ip_address

    # # Get and print the IP address
    # my_ip_address = get_ip_address()
    # print(f"My IP Address: {my_ip_address}")    

   