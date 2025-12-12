import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { usePeople } from "@/services/people";
import { AlertTriangle, AlertCircle, Info, GitBranch, Code, Briefcase, TrendingUp, Loader2 } from "lucide-react";

const PersonDashboard = () => {
  const { data: people, isLoading, error } = usePeople();
  const [selectedPersonId, setSelectedPersonId] = useState<string | null>(null);

  // Select first person once data is loaded
  const selectedPerson = people?.find(p => p.id === selectedPersonId) || people?.[0];

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

  const getExpertiseColor = (level: number) => {
    if (level >= 90) return "text-green-600";
    if (level >= 70) return "text-blue-600";
    if (level >= 50) return "text-yellow-600";
    return "text-gray-600";
  };

  const getActivityBadge = (commits: number) => {
    if (commits === 0) return <Badge variant="destructive">Inativo</Badge>;
    if (commits < 20) return <Badge variant="secondary">Baixa</Badge>;
    if (commits < 40) return <Badge className="bg-yellow-500">Média</Badge>;
    return <Badge className="bg-green-500">Alta</Badge>;
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
        <span className="ml-2 text-gray-600">Carregando pessoas...</span>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertTriangle className="w-4 h-4" />
        <AlertDescription>
          Erro ao carregar pessoas: {error instanceof Error ? error.message : 'Erro desconhecido'}
        </AlertDescription>
      </Alert>
    );
  }

  if (!people || people.length === 0) {
    return (
      <Alert>
        <Info className="w-4 h-4" />
        <AlertDescription>Nenhuma pessoa encontrada.</AlertDescription>
      </Alert>
    );
  }

  if (!selectedPerson) {
    return null;
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {people.map((person) => (
          <Card
            key={person.id}
            className={`cursor-pointer transition-all hover:shadow-lg ${
              selectedPerson.id === person.id ? "border-2 border-blue-200" : ""
            }`}
            onClick={() => setSelectedPersonId(person.id)}
          >
            <CardHeader className="pb-3">
              <div className="flex items-start gap-3">
                <Avatar className="w-12 h-12">
                  <AvatarFallback className="bg-blue-500 text-white font-semibold">
                    {person.avatar}
                  </AvatarFallback>
                </Avatar>
                <div className="flex-1">
                  <CardTitle className="text-lg">{person.name}</CardTitle>
                  <CardDescription className="text-xs">{person.email}</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Atividade recente:</span>
                  {getActivityBadge(person.recentActivity)}
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Repositórios:</span>
                  <span className="font-medium">{person.repositories.length}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Tecnologias:</span>
                  <span className="font-medium">{person.technologies.length}</span>
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
              Alertas e Observações
            </CardTitle>
            <CardDescription>
              Indicadores para {selectedPerson.name}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {selectedPerson.alerts.map((alert, index) => (
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
              <Code className="w-5 h-5 text-purple-500" />
              Tecnologias e Expertise
            </CardTitle>
            <CardDescription>
              Nível de conhecimento técnico
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {selectedPerson.technologies.map((tech, index) => (
                <div key={index} className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span className="font-medium">{tech.name}</span>
                    <span className={`font-bold ${getExpertiseColor(tech.level)}`}>
                      {tech.level}%
                    </span>
                  </div>
                  <Progress value={tech.level} className="h-2" />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <GitBranch className="w-5 h-5 text-blue-500" />
              Repositórios Principais
            </CardTitle>
            <CardDescription>
              Contribuições e nível de expertise
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {selectedPerson.repositories.map((repo, index) => (
                <div key={index} className="space-y-2 p-3 bg-gray-50 rounded-lg">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h4 className="font-semibold text-sm">{repo.name}</h4>
                      <p className="text-xs text-gray-500 mt-0.5">
                        Última atividade: {repo.lastActivity}
                      </p>
                    </div>
                    <Badge variant="outline" className="text-xs">
                      {repo.commits} commits
                    </Badge>
                  </div>
                  <div className="space-y-1">
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-600">Expertise</span>
                      <span className={`font-bold ${getExpertiseColor(repo.expertise)}`}>
                        {repo.expertise}%
                      </span>
                    </div>
                    <Progress value={repo.expertise} className="h-1.5" />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Briefcase className="w-5 h-5 text-green-500" />
              Domínios de Negócio
            </CardTitle>
            <CardDescription>
              Áreas de conhecimento funcional
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {selectedPerson.domains.map((domain, index) => (
                <Badge key={index} variant="secondary" className="text-sm">
                  {domain}
                </Badge>
              ))}
            </div>
            <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
              <div className="flex items-start gap-2">
                <TrendingUp className="w-5 h-5 text-blue-600 mt-0.5" />
                <div>
                  <h4 className="font-semibold text-sm text-blue-900">
                    Atividade nos Últimos 30 Dias
                  </h4>
                  <p className="text-2xl font-bold text-blue-600 mt-1">
                    {selectedPerson.recentActivity} commits
                  </p>
                  <p className="text-xs text-blue-700 mt-1">
                    {selectedPerson.recentActivity === 0
                      ? "Sem atividade recente"
                      : selectedPerson.recentActivity < 20
                      ? "Atividade baixa"
                      : selectedPerson.recentActivity < 40
                      ? "Atividade moderada"
                      : "Alta atividade"}
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default PersonDashboard;