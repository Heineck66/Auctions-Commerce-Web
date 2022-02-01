
from auctions.models import Watchitem


def add_watch_num(request):
    context = {
        'watchlength': len(Watchitem.objects.all().filter(user=request.user.id))
    }
    return context
