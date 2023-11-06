from django.shortcuts import render
from .serializers import CommitteeSerializer, CommitteeMembersSerializer, CommitteeMembershipSerializer
from .models import Committee, CommitteeMembership
from rest_framework import viewsets, permissions


class CommitteeViewSet(viewsets.ModelViewSet):
    lookup_field = "name__iexact"
    queryset = Committee.objects.all()
    serializer_class = CommitteeSerializer
    permission_classes = [permissions.IsAuthenticated]


class CommitteeMembersViewSet(viewsets.ModelViewSet):
    lookup_field = "name__iexact"
    queryset = Committee.objects.all()
    serializer_class = CommitteeMembersSerializer
    permission_classes = [permissions.IsAuthenticated]


class CommitteeMembershipViewSet(viewsets.ModelViewSet):
    lookup_field = "user"
    queryset = CommitteeMembership.objects.all()
    serializer_class = CommitteeMembershipSerializer
    permission_classes = [permissions.IsAuthenticated]
