import { promises as fs } from 'fs';
import path from 'path';

const DATA_FILE = path.join(process.cwd(), 'data', 'agents.json');

export interface AgentAddress {
  street: string;
  city: string;
  state: string;
  pincode: string;
  country: string;
}

export interface Agent {
  id: string;
  name: string;
  category: string;
  description: string;
  address: AgentAddress; // Structured address
  endpoint: string;
  registeredAt: string;
}

async function ensureDataFile() {
  try {
    await fs.access(DATA_FILE);
  } catch {
    await fs.writeFile(DATA_FILE, '[]', 'utf-8');
  }
}

export async function getAgents(): Promise<Agent[]> {
  await ensureDataFile();
  const data = await fs.readFile(DATA_FILE, 'utf-8');
  return JSON.parse(data);
}

export async function addAgent(agent: Omit<Agent, 'id' | 'registeredAt'>): Promise<Agent> {
  const agents = await getAgents();
  const newAgent: Agent = {
    ...agent,
    id: `agent_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    registeredAt: new Date().toISOString(),
  };
  agents.push(newAgent);
  await fs.writeFile(DATA_FILE, JSON.stringify(agents, null, 2), 'utf-8');
  return newAgent;
}

export interface SearchFilters {
  query?: string;
  category?: string;
  pincode?: string;
  city?: string;
  state?: string;
}

export async function searchAgents(filters: SearchFilters): Promise<Agent[]> {
  const agents = await getAgents();
  const { query, category, pincode, city, state } = filters;

  return agents.filter((agent) => {
    let matches = true;

    if (category) {
      matches = matches && agent.category.toLowerCase() === category.toLowerCase();
    }

    if (pincode) {
      matches = matches && agent.address.pincode === pincode;
    }

    if (city) {
      matches = matches && agent.address.city.toLowerCase() === city.toLowerCase();
    }

    if (state) {
      matches = matches && agent.address.state.toLowerCase() === state.toLowerCase();
    }

    if (query) {
      const q = query.toLowerCase();
      const textMatch =
        agent.name.toLowerCase().includes(q) ||
        agent.description.toLowerCase().includes(q) ||
        agent.address.street.toLowerCase().includes(q) ||
        agent.address.city.toLowerCase().includes(q);
      matches = matches && textMatch;
    }

    return matches;
  });
}
