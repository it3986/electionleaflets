from datetime import datetime
import re

from django.views.generic import DetailView, ListView
from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from uk_political_parties.models import Party
from leaflets.models import Leaflet


class PartyList(ListView):
    def get_queryset(self):

        queryset = Party.objects.annotate(
            num_leaflets=Count("leaflet")
        ).order_by("-num_leaflets", "party_name")
        return queryset

    template_name = "parties/party_list.html"


class PartyView(DetailView):
    model = Party

    def get_context_data(self, **kwargs):
        context = super(PartyView, self).get_context_data(**kwargs)
        id = re.sub(r"[^0-9]", "", self.kwargs["pk"])
        qs = Leaflet.objects.filter(
            publisher_party=self.kwargs["pk"]
        ) | Leaflet.objects.filter(ynr_party_id="party:{}".format(id))

        paginator = Paginator(qs, 60)
        page = self.request.GET.get("page")

        if not page or page == 1:
            if qs:
                context["last_leaflet_days"] = (
                    datetime.now() - qs[0].date_uploaded
                ).days

        try:
            context["party_leaflets"] = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            context["party_leaflets"] = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            context["party_leaflets"] = paginator.page(paginator.num_pages)

        return context

    template_name = "parties/party_detail.html"
