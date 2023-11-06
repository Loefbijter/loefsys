from django.urls import include, path
from rest_framework import routers
from .views import CommitteeViewSet, CommitteeMembersViewSet, CommitteeMembershipViewSet

app_name = "committees"

router = routers.DefaultRouter()
router.register(r'index', CommitteeViewSet)
router.register(r'members', CommitteeMembersViewSet, basename="member")
router.register(r'memberships', CommitteeMembershipViewSet, basename="membership")

# Wire up our API using automatic URL routing.
urlpatterns = [
    path('', include(router.urls)),
]
