from django.views.generic import View
from django.utils.html import escape
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse

from ckeditor_uploader.backends import get_backend
from ckeditor_uploader.utils import storage

from .oss import get_upload_file_info, upload_file, get_image_url_by_fiel_path

import uuid


class ImageUploadView(View):
    http_method_names = ["post"]

    def post(self, request, **kwargs):
        uploaded_file = request.FILES["upload"]

        backend = get_backend()

        ck_func_num = request.GET.get("CKEditorFuncNum")
        if ck_func_num:
            ck_func_num = escape(ck_func_num)

        filewrapper = backend(storage, uploaded_file)
        allow_nonimages = getattr(settings, "CKEDITOR_ALLOW_NONIMAGE_FILES", True)
        # Throws an error when an non-image file are uploaded.
        if not filewrapper.is_image and not allow_nonimages:
            return HttpResponse(
                """
                <script type='text/javascript'>
                window.parent.CKEDITOR.tools.callFunction({}, '', 'Invalid file type.');
                </script>""".format(
                    ck_func_num
                )
            )

        file_name = "{}-{}".format(uuid.uuid4().hex, uploaded_file.name)
        file_path = "ckeditor/{}".format(file_name)
        print(file_name)
        print(file_path)
        resp = get_upload_file_info(file_path)
        upload_file(
            resp.get('url'),
            file_path,
            resp.get('authorization'),
            resp.get('token'),
            resp.get('cos_file_id'),
            uploaded_file
        )
        file_url = get_image_url_by_fiel_path(file_path)

        if ck_func_num:
            # Respond with Javascript sending ckeditor upload url.
            return HttpResponse(
                """
            <script type='text/javascript'>
                window.parent.CKEDITOR.tools.callFunction({}, '{}');
            </script>""".format(
                    ck_func_num, file_url
                )
            )
        else:
            retdata = {"url": file_url, "uploaded": "1", "fileName": file_name}
            return JsonResponse(retdata)

upload = csrf_exempt(ImageUploadView.as_view())
