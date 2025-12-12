import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { repositories } from "@/data/mockData";
import { AlertTriangle, AlertCircle, Info, GitBranch, Users, Activity, TrendingUp } from "lucide-react";

const RepositoryDashboard = () => {
  const [selectedRepo, setSelectedRepo] = useState(repositories[0]);

  const getActivityColor = (activity: string) => {
    switch (activity) {
      case "high": return "bg-green-500";
      case "medium": return "bg-yellow-500";
      case "low": return "bg-orange-500";
      case "stale": return "bg-red-500";
      default: return "bg-gray-500";
    }
  };

  const getActivityLabel = (activity: string) => {
    switch (activity) {
      case "high": return "Alta";
      case "medium": return "Média";
      case "low": return "Baixa";
      case "stale": return "Obsoleto";
      default: return "Desconhecido";
    }
  };

  const getAlertIcon = (type: string) => {
    switch (type) {
      case "danger": return <AlertTriangle className="w-4 h-4" />;
      case "warning": return <AlertCircle className="w-4 h-4" />;
      case "info": return <Info className="w-4 h-4" />;
      default: return <Info className="w-4 h-4" />;
    }
  };

  const getAlertColor = (type: string) => {
    switch (type) {
      case "danger": return "border-red-500 bg-red-50 text-red-900";
      case "warning": return "border-yellow-500 bg-yellow-50 text-yellow-900";
      case "info": return "border-blue-500 bg-blue-50 text-blue-900";
      default: return "border-gray-500 bg-gray-50 text-gray-900";
    }
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {repositories.map((repo) => (
          <Card
            key={repo.id}
            className={`cursor-pointer transition-all hover:shadow-lg ${
              selectedRepo.id === repo.id ? "ring-2 ring-blue-500" : ""
            }`}
            onClick={() => setSelectedRepo(repo)}
          >
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <CardTitle className="text-lg flex items-center gap-2">
                    <GitBranch className="w-4 h-4" />
                    {repo.name}
                  </CardTitle>
                  <CardDescription className="mt-1 text-xs">
                    {repo.description}
                  </CardDescription>
                </div>
                <Badge className={`${getActivityColor(repo.activity)} text-white`}>
                  {getActivityLabel(repo.activity)}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Último commit:</span>
                  <span className="font-medium">{repo.lastCommit}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Total de commits:</span>
                  <span className="font-medium">{repo.totalCommits}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Contribuidores:</span>
                  <span className="font-medium">{repo.contributors}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-orange-500" />
              Alertas e Riscos
            </CardTitle>
            <CardDescription>
              Indicadores de risco para {selectedRepo.name}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {selectedRepo.alerts.map((alert, index) => (
              <Alert key={index} className={getAlertColor(alert.type)}>
                <div className="flex items-start gap-2">
                  {getAlertIcon(alert.type)}
                  <AlertDescription className="text-sm">
                    {alert.message}
                  </AlertDescription>
                </div>
              </Alert>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="w-5 h-5 text-blue-500" />
              Concentração de Conhecimento
            </CardTitle>
            <CardDescription>
              Distribuição de contribuições em {selectedRepo.name}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm font-medium">Índice de Concentração</span>
                <span className="text-sm font-bold text-orange-600">
                  {selectedRepo.knowledgeConcentration}%
                </span>
              </div>
              <Progress value={selectedRepo.knowledgeConcentration} className="h-2" />
              <p className="text-xs text-gray-500 mt-1">
                {selectedRepo.knowledgeConcentration > 60
                  ? "⚠️ Concentração alta - risco elevado"
                  : selectedRepo.knowledgeConcentration > 40
                  ? "⚡ Concentração moderada"
                  : "✅ Boa distribuição de conhecimento"}
              </p>
            </div>

            <div className="space-y-3 pt-2">
              <h4 className="text-sm font-semibold">Principais Contribuidores</h4>
              {selectedRepo.topContributors.map((contributor, index) => (
                <div key={index} className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span>{contributor.name}</span>
                    <span className="font-medium">{contributor.percentage}%</span>
                  </div>
                  <Progress value={contributor.percentage} className="h-1.5" />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-purple-500" />
              Hotspots de Código
            </CardTitle>
            <CardDescription>
              Arquivos mais frequentemente modificados
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {selectedRepo.hotspots.map((hotspot, index) => (
                <div key={index} className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span className="font-mono text-xs truncate flex-1">
                      {hotspot.path}
                    </span>
                    <span className="font-medium ml-2">{hotspot.changes} alterações</span>
                  </div>
                  <Progress value={(hotspot.changes / selectedRepo.hotspots[0].changes) * 100} className="h-1.5" />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="w-5 h-5 text-green-500" />
              Dependências
            </CardTitle>
            <CardDescription>
              Repositórios que costumam mudar juntos
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {selectedRepo.dependencies.length > 0 ? (
                selectedRepo.dependencies.map((dep, index) => (
                  <div
                    key={index}
                    className="flex items-center gap-2 p-2 bg-gray-50 rounded-md"
                  >
                    <GitBranch className="w-4 h-4 text-gray-500" />
                    <span className="text-sm font-medium">{dep}</span>
                  </div>
                ))
              ) : (
                <p className="text-sm text-gray-500">Nenhuma dependência identificada</p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default RepositoryDashboard;