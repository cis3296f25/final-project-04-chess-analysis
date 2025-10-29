from django.shortcuts import render
from django.core.files.storage import FileSystemStorage

# Create your views here.
def home(request):
    if request.method == 'POST' and request.FILES.get('uploaded_file'):
        uploaded_file = request.FILES['uploaded_file']

        # Save to /media/
        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)
        file_url = fs.url(filename)

        # (Optional) Access the file path on backend:
        file_path = fs.path(filename)
        print(f"Saved at: {file_path}")

        # You can open/read it here if you want:
        with open(file_path, 'r') as f:
            content = f.read()
            ######STOCKFUSH ANALYSIS LOGIC HERE########


        return render(request, 'home.html', {'file_url': file_url})
    return render(request, 'home.html')