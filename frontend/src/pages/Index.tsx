import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import RepositoryDashboard from "@/components/RepositoryDashboard";
import PersonDashboard from "@/components/PersonDashboard";
import PlanningAssistant from "@/components/PlanningAssistant";
import { GitBranch, Users, Sparkles } from "lucide-react";

const Index = () => {
  const [activeTab, setActiveTab] = useState("repositories");

  return (
    <Tabs value={activeTab} onValueChange={setActiveTab} className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center gap-3">
            <img
              src="/logo-512x512.png"
              alt="NexusPlanner Logo"
              className="h-10 w-10"
            />
            <h1 className="text-3xl font-bold text-gray-900">
              NexusPlanner
            </h1>
          </div>
          <p className="mt-2 text-sm text-gray-600">
            Planejamento de roadmap apoiados por IA
          </p>

          <TabsList className="grid w-full grid-cols-3 mt-6">
            <TabsTrigger value="repositories" className="flex items-center gap-2">
              <GitBranch className="w-4 h-4" />
              Repositórios
            </TabsTrigger>
            <TabsTrigger value="people" className="flex items-center gap-2">
              <Users className="w-4 h-4" />
              Pessoas
            </TabsTrigger>
            <TabsTrigger value="assistant" className="flex items-center gap-2">
              <Sparkles className="w-4 h-4" />
              Assistente de Planejamento
            </TabsTrigger>
          </TabsList>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <TabsContent value="repositories">
          <RepositoryDashboard />
        </TabsContent>

        <TabsContent value="people">
          <PersonDashboard />
        </TabsContent>

        <TabsContent value="assistant">
          <PlanningAssistant />
        </TabsContent>
      </main>
    </Tabs>
  );
};

export default Index;