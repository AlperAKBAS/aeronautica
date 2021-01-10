from django.shortcuts import render, HttpResponse, redirect

# Create your views here.
def home_view(request):
    if request.user.is_authenticated:
        return HttpResponse(
            f"""<h1>Home Page</h1><br><p>You are loggedin as {request.user.email}</p>"""
            )
    else:
        return redirect('web-register')