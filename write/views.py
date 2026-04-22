from django.http import JsonResponse
import json
from django.shortcuts import render,redirect
from .dashboard_llm_service import Dashboard_LLM_Service
from .models import HeartUser
from .models import Writing
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import check_password
from django.utils import timezone
from datetime import timedelta


def home(request):
    # If logged-in, go to dashboard
    if request.session.get("user_id"):
        return redirect("/dashboard/")
    return render(request, "home.html")


def aiwrite(request):
    return render(request,'aiwrite.html')

def dashboard(request):
    if not request.session.get("user_id"):
        return redirect("/")
    return render(request, "dashboard.html")




def admin_stats(request):
    total_users = HeartUser.objects.count()
    total_writings = Writing.objects.count()

    # Users joined in last 24 hours
    recent_users = HeartUser.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=1)
    ).count()

    return JsonResponse({
        "users": total_users,
        "writings": total_writings,
        "new_users_today": recent_users
    })


dashboard_llm = Dashboard_LLM_Service()

def generate_dashboard(request):
    mode = request.GET.get("mode")
    name = request.GET.get("name", "")
    desc = request.GET.get("desc", "")
    depth = request.GET.get("depth", "light")
    language = request.GET.get("language", "en")

    if not mode or not desc:
        return JsonResponse({"response": "Please write something."})

    result = dashboard_llm.generate(mode, name, desc, depth, language)

    # ✅ RETURN STRING ONLY
    return JsonResponse({"response": result})




@csrf_exempt
def signup_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=400)

    username = request.POST.get("username")
    email = request.POST.get("email")
    password = request.POST.get("password")

    if not username or not email or not password:
        return JsonResponse({"error": "Missing fields"}, status=400)

    if HeartUser.objects.filter(username=username).exists():
        return JsonResponse({"error": "Username already taken"}, status=400)

    if HeartUser.objects.filter(email=email).exists():
        return JsonResponse({"error": "Email already exists"}, status=400)

    user = HeartUser.objects.create(
        username=username,
        email=email,
        password=make_password(password),
    )

    request.session["user_id"] = user.id     # VERY IMPORTANT
    request.session["username"] = user.username

    return JsonResponse({"status": "ok"})


@csrf_exempt
def upload_avatar(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({"error": "Not logged in"}, status=403)

    user = HeartUser.objects.get(id=user_id)

    if "avatar" in request.FILES:
        user.avatar = request.FILES["avatar"]
        user.save()

        return JsonResponse({
            "status": "ok",
            "avatar_url": user.avatar.url
        })

    return JsonResponse({"error": "No file"})

@csrf_exempt
def get_avatar(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({"avatar": None})

    user = HeartUser.objects.get(id=user_id)

    return JsonResponse({
        "avatar": user.avatar.url if user.avatar else None
    })

@csrf_exempt
def profile_api(request):

    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({"error": "Not logged in"}, status=403)

    user = HeartUser.objects.get(id=user_id)

    return JsonResponse({
        "username": user.username,
        "email": user.email
    })

@csrf_exempt
def login_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=400)

    username = request.POST.get("username")
    password = request.POST.get("password")

    try:
        user = HeartUser.objects.get(username=username)
    except HeartUser.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=400)

    if not check_password(password, user.password):
        return JsonResponse({"error": "Wrong password"}, status=400)

    request.session["user_id"] = user.id
    request.session["username"] = user.username

    return JsonResponse({"status": "ok"})
@csrf_exempt
def logout_api(request):
    request.session.flush()
    return JsonResponse({"status": "logged_out"})

@csrf_exempt
def delete_account(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=400)

    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({"error": "Not logged in"}, status=400)

    try:
        user = HeartUser.objects.get(id=user_id)
        user.delete()
    except HeartUser.DoesNotExist:
        pass

    request.session.flush()   # remove session from server

    return JsonResponse({"status": "deleted"})



@csrf_exempt
def save_writing(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=400)

    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({"error": "Not logged in"}, status=403)

    tool = request.POST.get("tool")
    icon = request.POST.get("icon")
    nameInput = request.POST.get("nameInput")
    descInput = request.POST.get("descInput")
    depthInput = request.POST.get("depthInput")
    output = request.POST.get("output")

    if not output:
        return JsonResponse({"error": "Empty writing"}, status=400)

    user = HeartUser.objects.filter(id=user_id).first()

    # ✅ CHECK BEFORE SAVE
    existing = Writing.objects.filter(
        user=user,
        output=output
    ).first()

    if existing:
        return JsonResponse({"status": "exists"})

    # ✅ SAVE ONLY IF NOT EXISTS
    Writing.objects.create(
        user=user,
        tool=tool,
        icon=icon,
        nameInput=nameInput,
        descInput=descInput,
        depthInput=depthInput,
        output=output
    )

    return JsonResponse({"status": "saved"})





@csrf_exempt
def get_writings(request):

    user_id = request.session.get("user_id")

    writings = Writing.objects.filter(
        user_id=user_id
    ).order_by("-created_at")[:20]

    data = []

    for w in writings:

        preview = w.output[:60]
        if len(w.output) > 60:
            preview += "..."

        data.append({
            "id": w.id,
            "name": w.tool,
            "icon": w.icon,
            "preview": preview,
            "time": w.created_at.strftime("%b %d, %H:%M"),
            "nameInput": w.nameInput,
            "descInput": w.descInput,
            "depthInput": w.depthInput,
            "output": w.output
        })

    return JsonResponse({"recents": data})


@csrf_exempt
def delete_writing(request):

    data = json.loads(request.body)

    writing_id = data.get("id")

    user_id = request.session.get("user_id")

    Writing.objects.filter(
        id=writing_id,
        user_id=user_id
    ).delete()

    return JsonResponse({"status": "deleted"})


@csrf_exempt
def reset_app(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=400)

    user_id = request.session.get("user_id")

    if not user_id:
        return JsonResponse({"error": "Not logged in"}, status=403)

    Writing.objects.filter(user_id=user_id).delete()

    return JsonResponse({"status": "reset"})
