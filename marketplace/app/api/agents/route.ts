
import { NextRequest, NextResponse } from 'next/server';
import { getAgents, addAgent, searchAgents } from '@/lib/agents';

// GET /api/agents
// Search for agents.
// Query Params: ?query=...&category=...&pincode=...&city=...&state=...
export async function GET(request: NextRequest) {
    const searchParams = request.nextUrl.searchParams;
    const filters = {
        query: searchParams.get('query') || undefined,
        category: searchParams.get('category') || undefined,
        pincode: searchParams.get('pincode') || undefined,
        city: searchParams.get('city') || undefined,
        state: searchParams.get('state') || undefined,
    };

    // API Key Validation
    const apiKey = request.headers.get('x-api-key');
    const validKey = process.env.MARKETPLACE_API_KEY;

    if (!validatedApiKey(apiKey, validKey, request)) {
        return NextResponse.json({ error: 'Unauthorized: Invalid API Key' }, { status: 401 });
    }

    const agents = await searchAgents(filters);

    // Return standard JSON response
    return NextResponse.json({
        count: agents.length,
        agents: agents
    });
}

function validatedApiKey(headerKey: string | null, envKey: string | undefined, request: NextRequest): boolean {
    // Allow localhost requests for local development
    const host = request.headers.get('host') || '';
    if (host.includes('localhost') || host.includes('127.0.0.1')) {
        return true;
    }
    if (!envKey) return true; // Dev mode: if no key set, allow all
    return headerKey === envKey;
}

// POST /api/agents
// Register a new agent.
export async function POST(request: NextRequest) {
    try {
        const body = await request.json();

        // Detailed validation
        if (!body.name || !body.category || !body.endpoint || !body.address) {
            return NextResponse.json({ error: 'Missing required fields' }, { status: 400 });
        }

        const { address } = body;
        if (!address.street || !address.city || !address.state || !address.pincode || !address.country) {
            return NextResponse.json({ error: 'Invalid address structure. Required: street, city, state, pincode, country' }, { status: 400 });
        }

        const newAgent = await addAgent({
            name: body.name,
            category: body.category,
            description: body.description || '',
            address: body.address, // Expecting full object
            endpoint: body.endpoint,
        });

        return NextResponse.json(newAgent, { status: 201 });
    } catch (error) {
        console.error('Error registering agent:', error);
        return NextResponse.json(
            { error: 'Internal Server Error' },
            { status: 500 }
        );
    }
}

