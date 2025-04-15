# Frontend Integration with Next.js

The `zero-hunger` directory contains a modern Next.js frontend application that can be integrated with your Django backend API. This document explains how to set up and connect the two components.

## Architecture

The system uses a decoupled architecture:
- **Backend**: Django REST API
- **Frontend**: Next.js with TypeScript and Tailwind CSS

## Setup

### Prerequisites

- Node.js 18+ 
- pnpm (or npm/yarn)
- Django backend running with REST API endpoints

### Installation

1. Navigate to the frontend directory:
   ```bash
   cd zero-hunger
   ```

2. Install dependencies:
   ```bash
   pnpm install
   ```

3. Configure the API URL:
   Create a `.env.local` file in the zero-hunger directory:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000/api
   ```

4. Start the development server:
   ```bash
   pnpm dev
   ```

5. Build for production:
   ```bash
   pnpm build
   ```

## Connecting to the Django API

The frontend connects to the Django API using the Fetch API or Axios. Example:

```typescript
// Example API service using fetch
const API_URL = process.env.NEXT_PUBLIC_API_URL;

export async function login(username: string, password: string) {
  const response = await fetch(`${API_URL}/login/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password }),
  });
  
  if (!response.ok) {
    throw new Error('Login failed');
  }
  
  return response.json();
}

export async function getDonations(token: string) {
  const response = await fetch(`${API_URL}/donations/`, {
    headers: {
      'Authorization': `Token ${token}`,
    },
  });
  
  if (!response.ok) {
    throw new Error('Failed to fetch donations');
  }
  
  return response.json();
}
```

## Authentication

The Next.js frontend handles authentication by:

1. Storing tokens in secure HTTP-only cookies or local storage
2. Including the token in all API requests
3. Implementing protected routes using Next.js middleware

## Available Components

The frontend includes reusable components that match the Django application's features:

- User authentication forms (login, register)
- Donation creation and management
- Volunteer dashboard
- Admin controls
- Statistics and charts
- Responsive navigation
- User profiles

## Deployment Options

### Option 1: Separate Deployments

Deploy the Django backend and Next.js frontend separately:
- Django: PythonAnywhere, Render, Heroku, etc.
- Next.js: Vercel, Netlify, or any static hosting

### Option 2: Unified Deployment

Serve the Next.js app from the Django application:
1. Build the Next.js app
2. Copy the build output to the Django static files directory
3. Configure Django to serve the Next.js app at the root URL

## Development Workflow

1. Run both servers simultaneously during development:
   - Django on port 8000
   - Next.js on port 3000
   
2. Make API requests from Next.js to Django
   
3. Use CORS headers in Django to allow cross-origin requests

## Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Django REST Framework Documentation](https://www.django-rest-framework.org/)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs) 