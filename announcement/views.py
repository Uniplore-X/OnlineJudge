# coding=utf-8
from rest_framework.views import APIView

from utils.shortcuts import serializer_invalid_response, error_response, success_response

from account.models import User
from utils.shortcuts import paginate
from .models import Announcement
from .serializers import (CreateAnnouncementSerializer, AnnouncementSerializer,
                          EditAnnouncementSerializer)


class AnnouncementAdminAPIView(APIView):
    def post(self, request):
        """
        公告发布json api接口
        ---
        request_serializer: CreateAnnouncementSerializer
        """
        serializer = CreateAnnouncementSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            Announcement.objects.create(title=data["title"],
                                        content=data["content"],
                                        created_by=request.user)
            return success_response(u"公告发布成功！")
        else:
            return serializer_invalid_response(serializer)

    def put(self, request):
        """
        公告编辑json api接口
        ---
        request_serializer: EditAnnouncementSerializer
        response_serializer: AnnouncementSerializer
        """
        serializer = EditAnnouncementSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            try:
                announcement = Announcement.objects.get(id=data["id"])
            except Announcement.DoesNotExist:
                return error_response(u"该公告不存在！")
            announcement.title = data["title"]
            announcement.content = data["content"]
            announcement.visible = data["visible"]
            announcement.save()
            return success_response(AnnouncementSerializer(announcement).data)
        else:
            return serializer_invalid_response(serializer)


class AnnouncementAPIView(APIView):
    def get(self, request):
        """
        公告分页json api接口
        ---
        response_serializer: AnnouncementSerializer
        """
        announcement = Announcement.objects.all().order_by("-last_update_time")
        visible = request.GET.get("visible", None)
        if visible:
            announcement = announcement.filter(visible=(visible == "true"))
        return paginate(request, announcement, AnnouncementSerializer)