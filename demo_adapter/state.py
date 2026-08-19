"""Shared, read-only demo data seeded once and read by every per-domain adapter.

Splitting the monolithic demo adapter into one class per domain still leaves
several domains needing to agree on the same fake world: status's resources
reference facility's site ids, and account's project-membership is read by
other domains. Seeding that world once here -- instead of independently in
each domain's adapter -- keeps the per-domain adapters independently
swappable while still presenting one consistent demo.

v1 note: iri-api-python v1.2.0 has no `storage` domain (it's v2-only, see
the main branch), so this file carries no storage-domain state (locations,
access endpoints) here -- only the status-domain "storage_system"-type
Resource entries (hpss, cfs), which v1 does have.
"""
import datetime
import random

from app.routers.account import models as account_models
from app.routers.facility import models as facility_models
from app.routers.status import models as status_models
from app.types.models import Capability
from app.types.scalars import AllocationUnit

from .common import DEMO_USER, demo_uuid, utc_now


class DemoState:
    """Seeds and holds the fake facility/site/resource/project/location data shared across domains."""

    def __init__(self):
        self.user = DEMO_USER
        self.resources: list[status_models.Resource] = []
        self.incidents: list[status_models.Incident] = []
        self.events: list[status_models.Event] = []
        self.capabilities: dict[str, Capability] = {}
        self.projects: list[account_models.Project] = []
        self.project_allocations: list[account_models.ProjectAllocation] = []
        self.user_allocations: list[account_models.UserAllocation] = []
        self.facility: facility_models.Facility | None = None
        self.sites: list[facility_models.Site] = []
        self._init_state()

    def _init_state(self):
        now = utc_now()

        site1 = facility_models.Site(
            id=demo_uuid("site", "demo_site_1"),
            name="Demo Site 1",
            description="The first demo site",
            last_modified=now,
            short_name="DS1",
            operating_organization="Demo Org",
            country_name="USA",
            locality_name="Demo City",
            state_or_province_name="DC",
            latitude=36.173357,
            longitude=-234.51452,
            resource_ids=[],
        )

        site2 = facility_models.Site(
            id=demo_uuid("site", "demo_site_2"),
            name="Demo Site 2",
            description="The second demo site",
            last_modified=now,
            short_name="DS2",
            operating_organization="Demo Org",
            country_name="USA",
            locality_name="Example Town",
            state_or_province_name="ET",
            latitude=38.410558,
            longitude=-286.36999,
            resource_ids=[],
        )

        self.facility = facility_models.Facility(
            id=demo_uuid("facility", "demo_facility"),
            name="Demo Facility",
            description="A demo facility for testing the IRI Facility API",
            last_modified=now,
            short_name="DEMO",
            organization_name="Demo Organization",
            support_uri="https://support.demo.example",
            site_ids=[site1.id, site2.id],
        )

        self.sites = [site1, site2]

        day_ago = utc_now() - datetime.timedelta(days=1)
        self.capabilities = {
            "cpu": Capability(id=demo_uuid("capability", "cpu"), name="CPU Nodes", units=[AllocationUnit.node_hours]),
            "gpu": Capability(id=demo_uuid("capability", "gpu"), name="GPU Nodes", units=[AllocationUnit.node_hours]),
            "hpss": Capability(id=demo_uuid("capability", "hpss"), name="Tape Storage", units=[AllocationUnit.bytes, AllocationUnit.inodes]),
            "gpfs": Capability(id=demo_uuid("capability", "gpfs"), name="GPFS Storage", units=[AllocationUnit.bytes, AllocationUnit.inodes]),
        }

        pm = status_models.Resource(
            id=demo_uuid("resource", "perlmutter_compute_nodes"),
            site_id=site1.id,
            group="perlmutter",
            name="compute nodes",
            description="the perlmutter computer compute nodes",
            capability_ids=[
                self.capabilities["cpu"].id,
                self.capabilities["gpu"].id,
            ],
            current_status=status_models.Status.degraded,
            last_modified=day_ago,
            resource_type=status_models.ResourceType.compute,
            supported_endpoints=[status_models.Endpoint.compute],
        )

        hpss = status_models.Resource(
            id=demo_uuid("resource", "hpss"),
            site_id=site1.id,
            group="hpss",
            name="hpss",
            description="hpss tape storage",
            capability_ids=[self.capabilities["hpss"].id],
            current_status=status_models.Status.up,
            last_modified=day_ago,
            resource_type=status_models.ResourceType.storage,
            supported_endpoints=[status_models.Endpoint.filesystem],
            attributes={
                "schema_version": "1.0.0",
                "storage_type": "urn:doe-iri:storage:tape",
                "filesystem_technology": "hpss",
                "vendor": "IBM",
                "product": "HPSS",
            },
        )

        cfs = status_models.Resource(
            id=demo_uuid("resource", "cfs"),
            site_id=site1.id,
            group="cfs",
            name="cfs",
            description="cfs storage",
            capability_ids=[self.capabilities["gpfs"].id],
            current_status=status_models.Status.up,
            last_modified=day_ago,
            resource_type=status_models.ResourceType.storage,
            supported_endpoints=[status_models.Endpoint.filesystem],
            attributes={
                "schema_version": "1.0.0",
                "storage_type": "urn:doe-iri:storage:filesystem",
                "filesystem_technology": "gpfs",
                "vendor": "IBM",
                "product": "Spectrum Scale",
            },
        )

        login = status_models.Resource(
            id=demo_uuid("resource", "login_nodes"),
            site_id=site2.id,
            group="perlmutter",
            name="login nodes",
            description="the perlmutter computer login nodes",
            capability_ids=[],
            current_status=status_models.Status.degraded,
            last_modified=day_ago,
            resource_type=status_models.ResourceType.system,
        )

        iris = status_models.Resource(
            id=demo_uuid("resource", "iris"),
            site_id=site2.id,
            group="services",
            name="Iris",
            description="Iris webapp",
            capability_ids=[],
            current_status=status_models.Status.down,
            last_modified=day_ago,
            resource_type=status_models.ResourceType.website,
        )
        sfapi = status_models.Resource(
            id=demo_uuid("resource", "sfapi"),
            site_id=site2.id,
            group="services",
            name="sfapi",
            description="the Superfacility API",
            capability_ids=[],
            current_status=status_models.Status.up,
            last_modified=day_ago,
            resource_type=status_models.ResourceType.service,
        )

        self.resources = [pm, hpss, cfs, login, iris, sfapi]

        # Populate site resource_ids based on which resources are at each site
        site1.resource_ids = [r.id for r in self.resources if r.site_id == site1.id]
        site2.resource_ids = [r.id for r in self.resources if r.site_id == site2.id]

        self.projects = [
            account_models.Project(
                id=demo_uuid("project", "staff_research"),
                name="Staff research project",
                description="Compute and storage allocation for staff research use",
                user_ids=["gtorok"],
                last_modified=day_ago,
            ),
            account_models.Project(
                id=demo_uuid("project", "test_project"),
                name="Test project",
                description="Compute and storage allocation for testing use",
                user_ids=["gtorok"],
                last_modified=day_ago,
            ),
        ]

        for p in self.projects:
            for c in self.capabilities.values():
                pa = account_models.ProjectAllocation(
                    id=demo_uuid("project_allocation", f"{p.id}_{c.id}"),
                    project_id=p.id,
                    capability_id=c.id,
                    entries=[
                        account_models.AllocationEntry(
                            allocation=500 + random.random() * 500,
                            usage=100 + random.random() * 100,
                            unit=cu,
                        )
                        for cu in c.units
                    ],
                )
                self.project_allocations.append(pa)
                self.user_allocations.append(
                    account_models.UserAllocation(
                        id=demo_uuid("user_allocation", f"{pa.id}_gtorok"),
                        project_id=pa.project_id,
                        project_allocation_id=pa.id,
                        user_id="gtorok",
                        entries=[account_models.AllocationEntry(allocation=a.allocation / 10, usage=a.usage / 10, unit=a.unit) for a in pa.entries],
                    )
                )

        statuses = {r.name: status_models.Status.up for r in self.resources}
        last_incidents = {}
        d = datetime.datetime(2025, 3, 1, 10, 0, 0, tzinfo=datetime.timezone.utc)

        # generate some events and incidents
        # here every incident only has events from a single resource,
        # but in reality it is possible for an incident to have events from multiple resources
        for _i in range(0, 1000):
            r = random.choice(self.resources)
            status = statuses[r.name]
            event = status_models.Event(
                id=demo_uuid("event", f"{r.name}_{d.isoformat()}"),
                name=f"{r.name} is {status.value}",
                description=f"{r.name} is {status.value}",
                occurred_at=d,
                status=status,
                resource_id=r.id,
                last_modified=day_ago,
            )
            self.events.append(event)
            if r.name in last_incidents:
                inc = last_incidents[r.name]
                event.incident_id = inc.id
                inc.event_ids.append(event.id)
                if status == status_models.Status.up:
                    inc.end = d
                    del last_incidents[r.name]

            if random.random() > 0.9:
                if status == status_models.Status.down:
                    statuses[r.name] = status_models.Status.up
                else:
                    statuses[r.name] = status_models.Status.down
                    dstr = d.strftime("%Y-%m-%d %H:%M:%S.%f%z")
                    incident = status_models.Incident(
                        id=demo_uuid("incident", f"{r.name}_{dstr}"),
                        name=f"{r.name} incident at {dstr}",
                        description=f"{r.name} incident at {dstr}",
                        status=status_models.Status.down,
                        event_ids=[],
                        resource_ids=random.choices([r.id for r in self.resources], k=3),
                        start=d,
                        end=d,
                        type=random.choice(list(status_models.IncidentType)),
                        resolution=random.choice(list(status_models.Resolution)),
                        last_modified=d,
                    )
                    self.incidents.append(incident)
                    last_incidents[r.name] = incident

            d += datetime.timedelta(minutes=int(random.random() * 15 + 1))


STATE = DemoState()
