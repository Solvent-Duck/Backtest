import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4">
            Intervention Testing Platform
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Test if your supplements and health interventions actually work
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <Card>
            <CardHeader>
              <CardTitle>Import Health Data</CardTitle>
              <CardDescription>
                Connect your Apple Health data to get started
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600 mb-4">
                Export your Apple Health data and upload it to see your metrics
              </p>
              <Link href="/dashboard">
                <Button>Get Started</Button>
              </Link>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Track Interventions</CardTitle>
              <CardDescription>
                Log supplements, diet changes, and lifestyle modifications
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600 mb-4">
                Create interventions and track them over time
              </p>
              <Link href="/dashboard">
                <Button variant="outline">Learn More</Button>
              </Link>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Get Insights</CardTitle>
              <CardDescription>
                Statistical analysis shows what actually works
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600 mb-4">
                See before/after comparisons with statistical significance
              </p>
              <Link href="/dashboard">
                <Button variant="outline">View Results</Button>
              </Link>
            </CardContent>
          </Card>
        </div>

        <div className="text-center">
          <Link href="/dashboard">
            <Button size="lg">Go to Dashboard</Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
