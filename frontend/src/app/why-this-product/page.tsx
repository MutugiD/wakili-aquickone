"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import WakiliLogo from "@/components/WakiliLogo";
import {
  FileText,
  Search,
  PenTool,
  Shield,
  Zap,
  Users,
  Building2,
  Briefcase,
  CheckCircle,
  ChevronDown,
  MessageSquare,
  Target,
  FileCheck,
  UserCheck,
  Calendar,
  BookOpen,
  Database,
  Cpu,
  Globe
} from "lucide-react";

export default function WhyThisProduct() {
  return (
    <div className="min-h-screen bg-black text-white">
              {/* Header */}
        <header className="bg-black border-b border-gray-800 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-6">
              <Link href="/">
                <WakiliLogo size="md" />
              </Link>
              <nav className="hidden md:flex space-x-8">
                <div className="relative group">
                  <button className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors flex items-center">
                    Products
                    <ChevronDown className="w-4 h-4 ml-1" />
                  </button>
                  <div className="absolute top-full left-0 mt-2 w-64 bg-gray-900 rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                    <div className="py-2">
                      <Link href="#research" className="block px-4 py-2 text-gray-300 hover:bg-gray-800 hover:text-white">
                        AI Research Agent
                      </Link>
                      <Link href="#workflows" className="block px-4 py-2 text-gray-300 hover:bg-gray-800 hover:text-white">
                        Agentic Workflows
                      </Link>
                      <Link href="#knowledge" className="block px-4 py-2 text-gray-300 hover:bg-gray-800 hover:text-white">
                        Knowledge Integrations
                      </Link>
                      <Link href="#drafting" className="block px-4 py-2 text-gray-300 hover:bg-gray-800 hover:text-white">
                        Document Drafting
                      </Link>
                    </div>
                  </div>
                </div>
                <div className="relative group">
                  <button className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors flex items-center">
                    Solutions
                    <ChevronDown className="w-4 h-4 ml-1" />
                  </button>
                  <div className="absolute top-full left-0 mt-2 w-64 bg-gray-900 rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                    <div className="py-2">
                      <Link href="#pain-points" className="block px-4 py-2 text-gray-300 hover:bg-gray-800 hover:text-white">
                        Legal Pain Points
                      </Link>
                      <Link href="#benefits" className="block px-4 py-2 text-gray-300 hover:bg-gray-800 hover:text-white">
                        Benefits & ROI
                      </Link>
                      <Link href="#use-cases" className="block px-4 py-2 text-gray-300 hover:bg-gray-800 hover:text-white">
                        Use Cases
                      </Link>
                    </div>
                  </div>
                </div>
                <Link href="/why-this-product" className="text-white px-3 py-2 rounded-md text-sm font-medium">
                  Why This Product
                </Link>
              </nav>
              <div className="flex items-center space-x-4">
                <Link href="/demo" className="bg-white text-black px-6 py-3 rounded-lg font-semibold hover:bg-gray-200 transition-colors">
                  Book Demo
                </Link>
              </div>
            </div>
          </div>
        </header>

      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center">
        {/* Background with gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-br from-gray-900 via-black to-gray-800"></div>

        {/* Content */}
        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left side - Text */}
            <div className="space-y-8">
              <motion.div
                initial={{ opacity: 0, x: -50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.8 }}
                className="space-y-6"
              >
                <p className="text-emerald-400 font-semibold tracking-wide uppercase text-sm">
                  Why use Wakili for your team
                </p>
                <h1 className="text-5xl md:text-7xl font-bold leading-tight">
                  Join the legal industry&apos;s AI
                  <span className="block text-emerald-400">revolution.</span>
                </h1>
                <p className="text-xl text-gray-300 leading-relaxed max-w-2xl">
                  Smart technology is reshaping legal processes for the future. Leverage a comprehensive legal AI platform to maintain a competitive edge in Kenya&apos;s evolving legal landscape.
                </p>
              </motion.div>

              {/* CTA Buttons */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.3 }}
                className="flex flex-col sm:flex-row gap-4"
              >
                <Link href="/demo" className="bg-white text-black px-8 py-4 rounded-lg font-semibold hover:bg-gray-200 transition-all duration-300 text-center">
                  Book Demo
                </Link>
                <Link href="/upgrade" className="border border-white text-white px-8 py-4 rounded-lg font-semibold hover:bg-white hover:text-black transition-all duration-300 text-center">
                  Explore Pricing
                </Link>
              </motion.div>
            </div>

            {/* Right side - Image placeholder for Kenyan professionals */}
            <motion.div
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="relative"
            >
              <div className="bg-gradient-to-br from-emerald-500/20 to-blue-500/20 rounded-2xl p-8 backdrop-blur-sm border border-gray-700">
                <div className="aspect-square bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl flex items-center justify-center">
                  <div className="text-center space-y-4">
                    <div className="w-24 h-24 bg-emerald-500/20 rounded-full flex items-center justify-center mx-auto">
                      <Users className="w-12 h-12 text-emerald-400" />
                    </div>
                    <p className="text-gray-300 font-medium">Kenyan Legal Professionals</p>
                    <p className="text-sm text-gray-400">Modern legal practice with AI assistance</p>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* About Wakili Section */}
      <section id="about" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <div className="text-sm font-semibold text-blue-600 uppercase tracking-wide mb-4">
                ABOUT WAKILI: A QUICK ONE
              </div>
              <h2 className="text-3xl font-bold text-gray-900 mb-6">
                The Future of Legal Practice is Here
              </h2>
              <p className="text-lg text-gray-600 mb-6">
                Wakili: A Quick One is a cutting-edge AI intervention and acceleration platform specifically designed for the legal industry.
                We understand the unique challenges faced by legal professionals and have built a comprehensive solution that transforms
                how legal work is conducted in the modern era.
              </p>
              <p className="text-lg text-gray-600 mb-8">
                Our platform combines advanced artificial intelligence with deep legal domain expertise to automate routine tasks,
                enhance research capabilities, and streamline document workflows. We&apos;re committed to helping legal professionals
                focus on what matters most - delivering exceptional legal services to their clients while maximizing efficiency and accuracy.
              </p>
              <div className="flex items-center text-blue-600 font-semibold">
                <Calendar className="w-5 h-5 mr-2" />
                <span>Trusted by leading law firms worldwide</span>
              </div>
            </div>

            <div className="bg-gradient-to-br from-blue-50 to-indigo-100 rounded-lg p-8">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Our Mission</h3>
              <p className="text-gray-700 mb-6">
                To revolutionize legal practice through intelligent automation, enabling legal professionals to work more efficiently,
                accurately, and strategically while maintaining the highest standards of legal excellence.
              </p>
              <div className="space-y-4">
                <div className="flex items-center">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mr-3">
                    <Search className="w-4 h-4 text-blue-600" />
                  </div>
                  <span className="text-gray-700 font-medium">AI-powered legal research</span>
                </div>
                <div className="flex items-center">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mr-3">
                    <FileText className="w-4 h-4 text-blue-600" />
                  </div>
                  <span className="text-gray-700 font-medium">Intelligent document processing</span>
                </div>
                <div className="flex items-center">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mr-3">
                    <Zap className="w-4 h-4 text-blue-600" />
                  </div>
                  <span className="text-gray-700 font-medium">Automated workflow management</span>
                </div>
                <div className="flex items-center">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mr-3">
                    <Shield className="w-4 h-4 text-blue-600" />
                  </div>
                  <span className="text-gray-700 font-medium">Enterprise-grade security</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Platform Features Section */}
      <section className="py-20 bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">The platform for acceleration</h2>
            <p className="text-xl text-gray-300">Built for Kenyan legal professionals</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                number: "01",
                title: "Data Integration",
                subtitle: "Easily integrate with existing data sources",
                description: "Pick from pre-configured data source connectors and integrate with third-party applications or internal repositories.",
                icon: <Database className="w-8 h-8" />
              },
              {
                number: "02",
                title: "Model Choice",
                subtitle: "Choose any model to fit your use case",
                description: "Leverage off-the-shelf LLMs or proprietary models with our model-agnostic approach. Control costs with centralized token management.",
                icon: <Cpu className="w-8 h-8" />
              },
              {
                number: "03",
                title: "Enterprise Security",
                subtitle: "Deploy AI with enterprise-grade security built-in",
                description: "Wakili is built with an AI-first, modern architecture with security guardrails. The platform protects company data with role-based access controls.",
                icon: <Shield className="w-8 h-8" />
              },
              {
                number: "04",
                title: "Platform Approach",
                subtitle: "Leverage AI across your team with our comprehensive platform",
                description: "Build, deploy, and scale enterprise AI apps from a central platform. Gain complete observability and visibility with detailed audit management.",
                icon: <Globe className="w-8 h-8" />
              },
              {
                number: "05",
                title: "Get Started Quickly",
                subtitle: "Utilize flexible pricing and deployment options",
                description: "Get started with no friction with our simple pricing options. You can upgrade subscription plans as your team's requirements evolve.",
                icon: <Zap className="w-8 h-8" />
              }
            ].map((feature, index) => (
              <motion.div
                key={feature.number}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="bg-gray-800 rounded-xl p-8 hover:bg-gray-700 transition-all duration-300"
              >
                <div className="flex items-center mb-6">
                  <div className="w-12 h-12 bg-emerald-500/20 rounded-lg flex items-center justify-center mr-4">
                    <div className="text-emerald-400">
                      {feature.icon}
                    </div>
                  </div>
                  <span className="text-2xl font-bold text-emerald-400">{feature.number}</span>
                </div>
                <h3 className="text-xl font-bold text-white mb-2">{feature.title}</h3>
                <h4 className="text-lg font-semibold text-emerald-400 mb-3">{feature.subtitle}</h4>
                <p className="text-gray-300 leading-relaxed">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Legal Pain Points Section */}
      <section id="pain-points" className="py-20 bg-black">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-white mb-4">Common Legal Pain Points</h2>
            <p className="text-lg text-gray-300">We solve the challenges that slow down your legal practice</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              {
                title: "Time-Consuming Research",
                description: "Manual legal research takes hours, reducing productivity and increasing costs. Lawyers spend 40% of their time on research alone.",
                icon: <Target className="w-6 h-6" />,
                color: "blue"
              },
              {
                title: "Document Processing Delays",
                description: "Manual document review and analysis slows down case progression. Complex contracts can take days to review thoroughly.",
                icon: <MessageSquare className="w-6 h-6" />,
                color: "green"
              },
              {
                title: "Inconsistent Workflows",
                description: "Lack of standardized processes leads to errors and inefficiencies. Different lawyers handle similar cases differently.",
                icon: <Users className="w-6 h-6" />,
                color: "purple"
              },
              {
                title: "Limited Scalability",
                description: "Manual processes don't scale with growing case loads. Adding more lawyers doesn't always mean better efficiency.",
                icon: <Zap className="w-6 h-6" />,
                color: "orange"
              }
            ].map((point, index) => (
              <motion.div
                key={point.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="bg-gray-800 rounded-xl p-6 text-center hover:bg-gray-700 transition-all duration-300"
              >
                <div className="w-16 h-16 bg-emerald-500/20 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <div className="text-emerald-400">
                    {point.icon}
                  </div>
                </div>
                <h3 className="text-lg font-semibold text-white mb-3">{point.title}</h3>
                <p className="text-gray-300 text-sm leading-relaxed">{point.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* AI Research Agent Section */}
      <section id="research" className="py-20 bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-white mb-4">AI Research Agent</h2>
            <p className="text-lg text-gray-300">Revolutionary legal research powered by advanced AI</p>
          </div>

          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h3 className="text-2xl font-bold text-white mb-6">Intelligent Legal Research</h3>
              <p className="text-lg text-gray-300 mb-6">
                Our Kenyan Legal Research Agent provides instant access to comprehensive Kenyan case law, statutes, and legal precedents. Get accurate, jurisdiction-specific answers with full citations and precedent analysis.
              </p>
              <div className="space-y-4">
                <div className="flex items-start">
                  <CheckCircle className="w-5 h-5 text-emerald-500 mt-1 mr-3 flex-shrink-0" />
                  <div>
                    <h4 className="font-semibold text-white">Context-Aware Analysis</h4>
                    <p className="text-gray-300">Understands legal context and jurisdiction-specific requirements with deep legal expertise</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <CheckCircle className="w-5 h-5 text-emerald-500 mt-1 mr-3 flex-shrink-0" />
                  <div>
                    <h4 className="font-semibold text-white">Case Law Integration</h4>
                    <p className="text-gray-300">Access to comprehensive case law databases and precedents across multiple jurisdictions</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <CheckCircle className="w-5 h-5 text-emerald-500 mt-1 mr-3 flex-shrink-0" />
                  <div>
                    <h4 className="font-semibold text-white">Real-Time Updates</h4>
                    <p className="text-gray-300">Stay current with the latest legal developments and rulings from authoritative sources</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <CheckCircle className="w-5 h-5 text-emerald-500 mt-1 mr-3 flex-shrink-0" />
                  <div>
                    <h4 className="font-semibold text-white">Advanced Citation Management</h4>
                    <p className="text-gray-300">Automated citation verification and formatting for legal documents</p>
                  </div>
                </div>
              </div>
            </div>
            <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-8 shadow-lg border border-gray-700">
              <div className="text-center mb-6">
                <div className="w-16 h-16 bg-emerald-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <BookOpen className="w-8 h-8 text-emerald-400" />
                </div>
                <h4 className="text-xl font-semibold text-white mb-2">Kenyan Legal Research</h4>
                <p className="text-gray-300 text-sm">Powered by comprehensive Kenyan legal databases</p>
              </div>
              <div className="space-y-4">
                <button className="w-full flex items-center p-3 bg-gray-700 rounded-lg shadow-sm hover:shadow-md transition-all duration-200 hover:bg-gray-600 group">
                  <Database className="w-5 h-5 text-emerald-400 mr-3 group-hover:scale-110 transition-transform" />
                  <span className="text-gray-200 font-medium">Multi-jurisdiction case law analysis</span>
                  <ChevronDown className="w-4 h-4 text-emerald-400 ml-auto group-hover:rotate-180 transition-transform" />
                </button>
                <button className="w-full flex items-center p-3 bg-gray-700 rounded-lg shadow-sm hover:shadow-md transition-all duration-200 hover:bg-gray-600 group">
                  <FileCheck className="w-5 h-5 text-emerald-400 mr-3 group-hover:scale-110 transition-transform" />
                  <span className="text-gray-200 font-medium">Statute interpretation & compliance checking</span>
                  <ChevronDown className="w-4 h-4 text-emerald-400 ml-auto group-hover:rotate-180 transition-transform" />
                </button>
                <button className="w-full flex items-center p-3 bg-gray-700 rounded-lg shadow-sm hover:shadow-md transition-all duration-200 hover:bg-gray-600 group">
                  <Target className="w-5 h-5 text-emerald-400 mr-3 group-hover:scale-110 transition-transform" />
                  <span className="text-gray-200 font-medium">Precedent identification & relevance scoring</span>
                  <ChevronDown className="w-4 h-4 text-emerald-400 ml-auto group-hover:rotate-180 transition-transform" />
                </button>
                <button className="w-full flex items-center p-3 bg-gray-700 rounded-lg shadow-sm hover:shadow-md transition-all duration-200 hover:bg-gray-600 group">
                  <Globe className="w-5 h-5 text-emerald-400 mr-3 group-hover:scale-110 transition-transform" />
                  <span className="text-gray-200 font-medium">Kenyan legal framework insights</span>
                  <ChevronDown className="w-4 h-4 text-emerald-400 ml-auto group-hover:rotate-180 transition-transform" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Agentic Workflows Section */}
      <section id="workflows" className="py-20 bg-black">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-white mb-4">Smart Legal Workflows</h2>
            <p className="text-lg text-gray-300">Streamlined process from research to final document</p>
          </div>

          <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-8 shadow-xl border border-gray-700">
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[
                {
                  step: "1",
                  title: "Research",
                  subtitle: "Intent Analysis",
                  icon: <Search className="w-6 h-6" />
                },
                {
                  step: "2",
                  title: "Draft",
                  subtitle: "Document Creation",
                  icon: <PenTool className="w-6 h-6" />
                },
                {
                  step: "3",
                  title: "Validate",
                  subtitle: "Quality Check",
                  icon: <FileCheck className="w-6 h-6" />
                },
                {
                  step: "4",
                  title: "Review",
                  subtitle: "Human Approval",
                  icon: <UserCheck className="w-6 h-6" />
                }
              ].map((step, index) => (
                <motion.div
                  key={step.step}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  className="bg-gray-700 rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow border border-gray-600"
                >
                  <div className="flex items-center mb-4">
                    <div className="bg-emerald-100 rounded-full w-12 h-12 flex items-center justify-center mr-4">
                      <div className="text-emerald-600 font-bold text-lg">{step.step}</div>
                    </div>
                    <div className="text-emerald-600">
                      {step.icon}
                    </div>
                  </div>
                  <h3 className="text-xl font-bold text-white mb-1">{step.title}</h3>
                  <p className="text-emerald-400 font-medium">{step.subtitle}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Knowledge Integrations Section */}
      <section id="knowledge" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Knowledge Integrations</h2>
            <p className="text-lg text-gray-600">Seamless integration with your existing legal knowledge base</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                title: "Database Integration",
                description: "Connect to your existing case management systems and legal databases for seamless data access.",
                icon: <Database className="w-8 h-8" />,
                color: "blue"
              },
              {
                title: "AI Processing",
                description: "Advanced AI algorithms process and analyze your legal documents and case files.",
                icon: <Cpu className="w-8 h-8" />,
                color: "green"
              },
              {
                title: "Global Knowledge",
                description: "Access to global legal knowledge bases, international law, and cross-jurisdictional insights.",
                icon: <Globe className="w-8 h-8" />,
                color: "purple"
              }
            ].map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="bg-gray-50 rounded-lg p-8 text-center"
              >
                <div className={`w-16 h-16 bg-${feature.color}-100 rounded-lg flex items-center justify-center mx-auto mb-6`}>
                  <div className={`text-${feature.color}-600`}>
                    {feature.icon}
                  </div>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-4">{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Document Drafting Section */}
      <section id="drafting" className="py-20 bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-white mb-4">Legal Document Creation</h2>
            <p className="text-lg text-gray-300">Professional drafting with Kenyan legal expertise</p>
          </div>

          <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-8 shadow-xl border border-gray-700">
            <div className="grid lg:grid-cols-2 gap-12 items-center">
                              <div>
                  <h3 className="text-2xl font-bold text-white mb-6">Key Legal Drafting Principles</h3>
                  <div className="space-y-4">
                    <div className="flex items-center p-4 bg-gray-700 rounded-lg shadow-sm border border-gray-600">
                      <div className="w-10 h-10 bg-emerald-500/20 rounded-full flex items-center justify-center mr-4">
                        <FileText className="w-5 h-5 text-emerald-400" />
                      </div>
                      <div>
                        <h4 className="font-bold text-white">Clarity & Precision</h4>
                        <p className="text-gray-300 text-sm">Clear, unambiguous language</p>
                      </div>
                    </div>
                    <div className="flex items-center p-4 bg-gray-700 rounded-lg shadow-sm border border-gray-600">
                      <div className="w-10 h-10 bg-emerald-500/20 rounded-full flex items-center justify-center mr-4">
                        <Shield className="w-5 h-5 text-emerald-400" />
                      </div>
                      <div>
                        <h4 className="font-bold text-white">Legal Compliance</h4>
                        <p className="text-gray-300 text-sm">Kenyan law requirements</p>
                      </div>
                    </div>
                    <div className="flex items-center p-4 bg-gray-700 rounded-lg shadow-sm border border-gray-600">
                      <div className="w-10 h-10 bg-emerald-500/20 rounded-full flex items-center justify-center mr-4">
                        <CheckCircle className="w-5 h-5 text-emerald-400" />
                      </div>
                      <div>
                        <h4 className="font-bold text-white">Proper Citations</h4>
                        <p className="text-gray-300 text-sm">Accurate legal references</p>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="bg-gray-700 rounded-xl p-6 shadow-lg border border-gray-600">
                  <h4 className="text-xl font-bold text-white mb-6">Document Types</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-gray-600 rounded-lg p-4 text-center hover:bg-gray-500 transition-colors">
                      <FileText className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
                      <span className="font-semibold text-white">Demand Letters</span>
                    </div>
                    <div className="bg-gray-600 rounded-lg p-4 text-center hover:bg-gray-500 transition-colors">
                      <FileText className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
                      <span className="font-semibold text-white">Legal Complaints</span>
                    </div>
                    <div className="bg-gray-600 rounded-lg p-4 text-center hover:bg-gray-500 transition-colors">
                      <FileText className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
                      <span className="font-semibold text-white">Legal Briefs</span>
                    </div>
                    <div className="bg-gray-600 rounded-lg p-4 text-center hover:bg-gray-500 transition-colors">
                      <FileText className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
                      <span className="font-semibold text-white">Affidavits</span>
                    </div>
                  </div>
                </div>
            </div>
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section id="benefits" className="py-20 bg-black">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-white mb-4">Why Choose Wakili</h2>
            <p className="text-lg text-gray-300">Agent-driven efficiency for modern legal practice</p>
          </div>

          <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-8 shadow-xl border border-gray-700">
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              {[
                {
                  number: "70%",
                  title: "Time Saved",
                  icon: <Zap className="w-8 h-8" />
                },
                {
                  number: "90%",
                  title: "Accuracy",
                  icon: <Target className="w-8 h-8" />
                },
                {
                  number: "60%",
                  title: "Cost Reduction",
                  icon: <Building2 className="w-8 h-8" />
                },
                {
                  number: "100%",
                  title: "Compliance",
                  icon: <Shield className="w-8 h-8" />
                }
              ].map((benefit, index) => (
                <motion.div
                  key={benefit.title}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  className="bg-gray-700 rounded-xl p-6 text-center shadow-lg hover:shadow-xl transition-shadow border border-gray-600"
                >
                  <div className="w-12 h-12 bg-emerald-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                    <div className="text-emerald-400">
                      {benefit.icon}
                    </div>
                  </div>
                  <div className="text-3xl font-bold text-emerald-400 mb-2">{benefit.number}</div>
                  <h3 className="text-lg font-bold text-white">{benefit.title}</h3>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Use Cases Section */}
      <section id="use-cases" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Use Cases</h2>
            <p className="text-lg text-gray-600">Real-world applications of Wakili: A Quick One</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              { title: "Law Firms", icon: <Building2 className="w-8 h-8" />, number: "01" },
              { title: "In-House Counsel", icon: <Briefcase className="w-8 h-8" />, number: "02" },
              { title: "Legal Operations", icon: <Zap className="w-8 h-8" />, number: "03" },
              { title: "Business Users", icon: <Users className="w-8 h-8" />, number: "04" }
            ].map((useCase, index) => (
              <motion.div
                key={useCase.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="text-center group cursor-pointer"
              >
                <div className="bg-white rounded-lg p-8 shadow-sm hover:shadow-md transition-shadow">
                  <div className="text-blue-600 mb-4 flex justify-center">
                    {useCase.icon}
                  </div>
                  <div className="text-sm text-gray-500 mb-2">{useCase.number}</div>
                  <h3 className="text-lg font-semibold text-gray-900">{useCase.title}</h3>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-blue-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-6">Ready to Transform Your Legal Practice?</h2>
          <p className="text-xl text-blue-100 mb-8 max-w-3xl mx-auto">
            Join leading law firms worldwide who are already using Wakili: A Quick One to revolutionize their legal workflows.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/demo"
              className="bg-white text-blue-600 px-8 py-4 rounded-lg font-semibold hover:bg-gray-100 transition-colors text-lg"
            >
              Book a Demo
            </Link>
            <Link
              href="/upgrade"
              className="bg-transparent text-white border-2 border-white px-8 py-4 rounded-lg font-semibold hover:bg-white hover:text-blue-600 transition-colors text-lg"
            >
              View Pricing
            </Link>
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="py-20 bg-gradient-to-br from-gray-900 to-black">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="space-y-8"
          >
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
              Upgrade your workflow.
            </h2>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/demo" className="bg-white text-black px-8 py-4 rounded-lg font-semibold hover:bg-gray-200 transition-all duration-300">
                Book Demo
              </Link>
              <Link href="/upgrade" className="border border-white text-white px-8 py-4 rounded-lg font-semibold hover:bg-white hover:text-black transition-all duration-300">
                Explore Pricing
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-black text-white py-12 border-t border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <WakiliLogo size="sm" showTagline={true} />
              <p className="mt-4 text-gray-400">
                Revolutionizing legal practice through intelligent AI intervention and acceleration.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Products</h3>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="#research" className="hover:text-white transition-colors">AI Research Agent</Link></li>
                <li><Link href="#workflows" className="hover:text-white transition-colors">Agentic Workflows</Link></li>
                <li><Link href="#knowledge" className="hover:text-white transition-colors">Knowledge Integrations</Link></li>
                <li><Link href="#drafting" className="hover:text-white transition-colors">Document Drafting</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Solutions</h3>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="#pain-points" className="hover:text-white transition-colors">Legal Pain Points</Link></li>
                <li><Link href="#benefits" className="hover:text-white transition-colors">Benefits & ROI</Link></li>
                <li><Link href="#use-cases" className="hover:text-white transition-colors">Use Cases</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Contact</h3>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="/demo" className="hover:text-white transition-colors">Book Demo</Link></li>
                <li><Link href="/upgrade" className="hover:text-white transition-colors">Pricing</Link></li>
                <li><a href="mailto:dennismutugi@gmail.com" className="hover:text-white transition-colors">Email Us</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 Wakili: A Quick One. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}