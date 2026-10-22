from app.routers.persistent_service import facility_adapter, models
from app.types.user import User
import datetime
import secrets
import yaml

from ..common import DemoAuthMixin

spin = models.Server(
    id="spin",
    display_name="NERSC Spin Server",
    capabilities=models.ServerCapabilities(
        supports_projects = True,
        project_required_for_namespace = True,
        supports_kubeconfig = True,
    ),
)

spin_r = models.Server(
    id="spin-r",
    display_name="NERSC Spin Restricted Server",
    capabilities=models.ServerCapabilities(
        supports_projects = True,
        project_required_for_namespace = True,
        supports_kubeconfig = True,
    ),
)

clusters = {
    "spin": [
        models.Cluster(
            id="nersc-spin-production",
            name="NERSC Spin Production Cluster",
            state=models.ClusterState.ACTIVE,
        ),
        models.Cluster(
            id="nersc-spin-development",
            name="NERSC Spin Restricted Development Cluster",
            state=models.ClusterState.ACTIVE,
        ),
    ],
    "spin-r": [
        models.Cluster(
            id="nersc-spin-r-production",
            name="NERSC Spin Production Cluster",
            state=models.ClusterState.ACTIVE,
        ),
        models.Cluster(
            id="nersc-spin-r-development",
            name="NERSC Spin Restricted Development Cluster",
            state=models.ClusterState.ACTIVE,
        ),
    ],
}
cluster_servers = {cluster.id:server_id for server_id,cluster_list in clusters.items() for cluster in cluster_list}
print("------------------")
print(cluster_servers)
print("------------------")
server_urls = {
    spin.id: "https://rancher2.spin.nersc.gov",
    spin_r.id: "https://rancher2-r.spin.nersc.gov"
}
CLUSTER_PATH = "/k8s/clusters"

class PersistentServiceDemoAdapter(DemoAuthMixin, facility_adapter.FacilityAdapter):

        async def get_servers(
            self: "PersistentServiceDemoAdapter",
            user: User,
        ) -> models.ServerList:
            if user.id == "gtorok":
                return models.ServerList(items=[spin, spin_r])
            else:
                return models.ServerList(items=[spin])


        async def get_clusters(
            self: "PersistentServiceDemoAdapter",
            user: User,
            server_id: str,
        ) -> models.ClusterList:
            return models.ClusterList(items=[cluster for cluster in clusters[server_id]])


        async def get_projects(
            self: "PersistentServiceDemoAdapter",
            user: User,
            server_id: str,
            cluster_id: str,
        ) -> models.ProjectList:
            return models.ProjectList(items=[
                # todo: this should be per server, per cluster and per user
                # for now just a static list
                models.Project(
                    id="nersc-spin-nstaff",
                    name="NERSC staff project",
                    role="admin" if user.id == "gtorok" else "user",
                ),
                models.Project(
                    id="nersc-spin-als",
                    name="ALS project",
                    role="user",
                ),
            ])


        async def create_namespace(
            self: "PersistentServiceDemoAdapter",
            user: User,
            server_id: str,
            cluster_id: str,
            namespace_request: models.NamespaceCreateRequest
        ) -> models.Namespace:
            return models.Namespace(
                id = namespace_request.id,
                cluster_id = cluster_id,
                project_id = namespace_request.project_id,
                labels = { "created_at": str(datetime.datetime.now()) },
            )


        async def create_kubeconfig(
            self: "PersistentServiceDemoAdapter",
            user: User,
            server_id: str,
            kubeconfig_request: models.KubeconfigRequest
        ) -> str:
            kubeconfig = {
                "apiVersion": "v1",
                "kind": "Config",
                "users": [{
                    "name": user.id,
                    "user": {
                        # todo: token should come from rancher
                        "token": f"kubeconfig-u-{secrets.token_urlsafe(8)}:{secrets.token_urlsafe(32)}",
                    }
                }],
                "clusters": {},
                "contexts": {},
            }

            cluster_list = clusters[server_id]
            for cluster in cluster_list:
                # todo: validation that clusters is not empty, etc.
                if not kubeconfig_request.cluster_ids or cluster.id in kubeconfig_request.cluster_ids:
                    server_id = cluster_servers[cluster.id]
                    kubeconfig["clusters"][cluster.id] = {
                        "name": cluster.id,
                        "cluster": {
                            "server": f"{server_urls[server_id]}{CLUSTER_PATH}/{cluster.id}",
                        }
                    }
                    kubeconfig["contexts"][cluster.id] = {
                        "name": cluster.id,
                        "context": {
                            "user": user.id,
                            "cluster": cluster.id,
                        }
                    }
            return yaml.safe_dump(kubeconfig, sort_keys=False, default_flow_style=False)
