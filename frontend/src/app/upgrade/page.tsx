'use client';

import Link from "next/link";
import { motion } from "framer-motion";
import { Check, Star, Zap, Shield, Users, Building2 } from "lucide-react";
import WakiliLogo from "../../components/WakiliLogo";

export default function UpgradePage() {
  const plans = [
    {
      name: "Starter",
      price: "$99",
      period: "/month",
      description: "Perfect for solo practitioners and small law firms",
      features: [
        "AI Research Agent (100 queries/month)",
        "Document Processing (50 documents/month)",
        "Basic Workflow Automation",
        "Email Support",
        "Standard Security",
        "1 User License"
      ],
      popular: false,
      icon: <Zap className="w-8 h-8" />
    },
    {
      name: "Professional",
      price: "$299",
      period: "/month",
      description: "Ideal for growing law firms and legal teams",
      features: [
        "AI Research Agent (500 queries/month)",
        "Document Processing (200 documents/month)",
        "Advanced Workflow Automation",
        "Agentic Workflows",
        "Priority Support",
        "Enhanced Security",
        "Up to 5 User Licenses",
        "Custom Templates"
      ],
      popular: true,
      icon: <Building2 className="w-8 h-8" />
    },
    {
      name: "Enterprise",
      price: "Custom",
      period: "",
      description: "For large law firms and corporate legal departments",
      features: [
        "Unlimited AI Research Queries",
        "Unlimited Document Processing",
        "Full Agentic Workflow Suite",
        "Custom AI Model Training",
        "Dedicated Support Team",
        "Enterprise Security & Compliance",
        "Unlimited User Licenses",
        "API Access",
        "Custom Integrations",
        "On-premise Deployment Option"
      ],
      popular: false,
      icon: <Shield className="w-8 h-8" />
    }
  ];

  const benefits = [
    {
      title: "Accelerate Case Processing",
      description: "Reduce document review time by up to 80% with AI-powered analysis",
      icon: <Zap className="w-6 h-6" />
    },
    {
      title: "Enhanced Research Capabilities",
      description: "Access comprehensive legal databases with intelligent search and citation generation",
      icon: <Star className="w-6 h-6" />
    },
    {
      title: "Streamlined Workflows",
      description: "Automate repetitive tasks and focus on high-value legal work",
      icon: <Users className="w-6 h-6" />
    },
    {
      title: "Enterprise Security",
      description: "Bank-level security with data encryption and compliance standards",
      icon: <Shield className="w-6 h-6" />
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <Link href="/">
              <WakiliLogo size="md" />
            </Link>
            <nav className="flex space-x-8">
              <Link href="/" className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors">
                Home
              </Link>
              <Link href="/demo" className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors">
                Request Demo
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-4xl md:text-5xl font-bold text-gray-900 mb-6"
          >
            Choose Your <span className="text-blue-600">Upgrade Path</span>
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="text-xl text-gray-600 mb-12 max-w-3xl mx-auto"
          >
            Select the perfect plan to accelerate your legal practice with AI-powered automation and intelligent workflows.
          </motion.p>
        </div>
      </section>

      {/* Pricing Plans */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-3 gap-8">
            {plans.map((plan, index) => (
              <motion.div
                key={plan.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className={`relative bg-white rounded-lg shadow-lg p-8 ${
                  plan.popular ? 'ring-2 ring-blue-600 transform scale-105' : ''
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <span className="bg-blue-600 text-white px-4 py-1 rounded-full text-sm font-semibold">
                      Most Popular
                    </span>
                  </div>
                )}

                <div className="text-center mb-8">
                  <div className="text-blue-600 mb-4 flex justify-center">
                    {plan.icon}
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">{plan.name}</h3>
                  <p className="text-gray-600 mb-4">{plan.description}</p>
                  <div className="mb-6">
                    <span className="text-4xl font-bold text-gray-900">{plan.price}</span>
                    <span className="text-gray-600">{plan.period}</span>
                  </div>
                </div>

                <ul className="space-y-4 mb-8">
                  {plan.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className="flex items-start">
                      <Check className="w-5 h-5 text-green-500 mt-0.5 mr-3 flex-shrink-0" />
                      <span className="text-gray-700">{feature}</span>
                    </li>
                  ))}
                </ul>

                <Link
                  href={plan.name === "Enterprise" ? "/demo" : "/demo"}
                  className={`w-full py-3 px-6 rounded-lg font-semibold text-center transition-colors ${
                    plan.popular
                      ? 'bg-blue-600 text-white hover:bg-blue-700'
                      : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
                  }`}
                >
                  {plan.name === "Enterprise" ? "Contact Sales" : "Get Started"}
                </Link>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Why Choose Wakili?</h2>
            <p className="text-lg text-gray-600">Experience the power of AI-driven legal automation</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {benefits.map((benefit, index) => (
              <motion.div
                key={benefit.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="text-center"
              >
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <div className="text-blue-600">
                    {benefit.icon}
                  </div>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{benefit.title}</h3>
                <p className="text-gray-600">{benefit.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-blue-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-6">Ready to Transform Your Legal Practice?</h2>
          <p className="text-xl text-blue-100 mb-8">Join thousands of legal professionals who trust Wakili for their AI automation needs.</p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/demo"
              className="bg-white text-blue-600 px-8 py-4 rounded-lg font-semibold hover:bg-gray-100 transition-colors text-lg"
            >
              Start Free Trial
            </Link>
            <Link
              href="/demo"
              className="bg-transparent text-white border-2 border-white px-8 py-4 rounded-lg font-semibold hover:bg-white hover:text-blue-600 transition-colors text-lg"
            >
              Schedule Demo
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-gray-400">&copy; 2024 Wakili. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}