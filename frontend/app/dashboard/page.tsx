"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import Link from "next/link";

export default function DashboardPage() {
  const [isUploading, setIsUploading] = useState(false);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    // TODO: Implement file upload
    console.log("Uploading file:", file.name);
    setTimeout(() => setIsUploading(false), 2000);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Dashboard</h1>
        <p className="text-gray-600">
          Manage your health data and interventions
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-6 mb-8">
        <Card>
          <CardHeader>
            <CardTitle>Upload Health Data</CardTitle>
            <CardDescription>
              Import your Apple Health export file
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Select Apple Health Export (.zip or .xml)
                </label>
                <input
                  type="file"
                  accept=".zip,.xml"
                  onChange={handleFileUpload}
                  disabled={isUploading}
                  className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                />
              </div>
              {isUploading && (
                <p className="text-sm text-gray-600">Uploading...</p>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Create Intervention</CardTitle>
            <CardDescription>
              Start tracking a new supplement or lifestyle change
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/dashboard/interventions/new">
              <Button className="w-full">New Intervention</Button>
            </Link>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Active Interventions</CardTitle>
          <CardDescription>
            Your currently tracked interventions
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-600">
            No active interventions yet. Create your first one to get started!
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
