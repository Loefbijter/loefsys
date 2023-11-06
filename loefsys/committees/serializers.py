# From https://www.django-rest-framework.org/tutorial/quickstart/
from .models import Committee, CommitteeMembership, User
from rest_framework import serializers


class CommitteeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Committee
        fields = ['name']


class CommitteeMembersSerializer(serializers.HyperlinkedModelSerializer):
    members = serializers.StringRelatedField(many=True)

    class Meta:
        model = Committee
        fields = ['name', 'members']


class CommitteeMembershipSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.StringRelatedField(many=False)
    committee = serializers.StringRelatedField(many=False)

    class Meta:
        model = CommitteeMembership
        fields = ['user', 'committee', 'since', 'until']
