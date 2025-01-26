from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.http import FileResponse
from PyPDF2 import PdfMerger
import os
import tempfile
from pathlib import Path
from .forms import MultipleFileUploadForm


class MultipleFileUploadPage(FormView):
    template_name = "pdf_merger/upload.html"
    form_class = MultipleFileUploadForm
    success_url = reverse_lazy("pdf_merger:multiple_file_upload")

    def form_valid(self, form):
        files = form.cleaned_data["files"]
        merger = PdfMerger()

        temp_file_paths = []
        merged_pdf_path = None

        try:
            # Save uploaded files to temporary files and append to merger
            for file in files:
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    tmp.write(file.read())
                    tmp.flush()
                    temp_file_paths.append(tmp.name)
                    merger.append(tmp.name)

            # Save merged PDF to the user's Downloads folder
            downloads_folder = Path.home() / "Downloads"
            if not downloads_folder.exists():
                downloads_folder.mkdir(parents=True, exist_ok=True)

            merged_pdf_path = downloads_folder / "merged_output.pdf"

            with open(merged_pdf_path, 'wb') as merged_pdf:
                merger.write(merged_pdf)

            merger.close()

            # Generate a download response
            pdf_file = open(merged_pdf_path, 'rb')  # ファイルを明示的にオープンし、クローズしない
            response = FileResponse(pdf_file, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="merged_output.pdf"'

            return response

        except Exception as e:
            print(f"An error occurred: {e}")
            raise e

        finally:
            # Cleanup all temporary files
            for path in temp_file_paths:
                try:
                    if os.path.exists(path):
                        os.unlink(path)
                except PermissionError:
                    print(f"PermissionError: Unable to delete {path}. It might be in use.")

            # Do not unlink merged_pdf_path to ensure it is available for response
