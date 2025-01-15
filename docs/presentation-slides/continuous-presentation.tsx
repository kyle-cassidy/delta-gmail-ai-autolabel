import React, { useEffect, useRef } from 'react';
import { Mail, Bot, Clock, AlertTriangle, Settings, CheckCircle, AlertCircle, ChevronDown } from 'lucide-react';
import { motion, useScroll, useTransform, useInView } from 'framer-motion';

const Header = () => {
  const { scrollY } = useScroll();
  const opacity = useTransform(scrollY, [0, 100], [0, 1]);
  
  return (
    <motion.div 
      style={{ opacity }}
      className="fixed top-0 left-0 right-0 bg-white/80 backdrop-blur-md z-50 border-b border-blue-100"
    >
      <nav className="max-w-6xl mx-auto p-4">
        <div className="flex justify-between items-center">
          <motion.div 
            initial={{ x: -20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 text-transparent bg-clip-text"
          >
            Delta Gmail AI
          </motion.div>
          <div className="flex space-x-6">
            {['Challenge', 'Solution', 'How It Works', 'Impact', '2024-2025'].map((item) => (
              <motion.button
                key={item}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="text-blue-600 hover:text-blue-800 font-medium"
              >
                {item}
              </motion.button>
            ))}
          </div>
        </div>
      </nav>
    </motion.div>
  );
};

const ScrollIndicator = () => (
  <motion.div
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay: 2, duration: 1, repeat: Infinity }}
    className="absolute bottom-8 left-1/2 transform -translate-x-1/2 text-blue-500"
  >
    <ChevronDown className="w-8 h-8 animate-bounce" />
  </motion.div>
);

const IntroSection = () => {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true });

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 pt-20 p-8 flex items-center relative">
      <motion.div
        ref={ref}
        initial={{ opacity: 0 }}
        animate={isInView ? { opacity: 1 } : {}}
        transition={{ duration: 0.8 }}
        className="max-w-4xl mx-auto"
      >
        <div className="text-center mb-12">
          <motion.h1
            initial={{ y: 20, opacity: 0 }}
            animate={isInView ? { y: 0, opacity: 1 } : {}}
            transition={{ delay: 0.2, duration: 0.8 }}
            className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 text-transparent bg-clip-text mb-4"
          >
            Delta Gmail AI Autolabel
          </motion.h1>
          <motion.p
            initial={{ y: 20, opacity: 0 }}
            animate={isInView ? { y: 0, opacity: 1 } : {}}
            transition={{ delay: 0.4, duration: 0.8 }}
            className="text-xl text-blue-700"
          >
            2024-2025: Transforming Email Management
          </motion.p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
          <motion.div
            initial={{ x: -50, opacity: 0 }}
            animate={isInView ? { x: 0, opacity: 1 } : {}}
            transition={{ delay: 0.6, duration: 0.8 }}
            className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 shadow-xl hover:shadow-2xl transition-shadow duration-300"
          >
            <h2 className="text-2xl font-semibold bg-gradient-to-r from-blue-600 to-indigo-600 text-transparent bg-clip-text mb-6">
              The Challenge
            </h2>
            <div className="space-y-6">
              <motion.div 
                className="flex items-start"
                whileHover={{ x: 5 }}
                transition={{ type: "spring", stiffness: 300 }}
              >
                <Mail className="w-6 h-6 text-blue-500 mr-3 mt-1 flex-shrink-0" />
                <p className="text-gray-700">
                  Managing registration emails for dozens of clients across 40 different state regulators
                </p>
              </motion.div>
              <motion.div 
                className="flex items-start"
                whileHover={{ x: 5 }}
                transition={{ type: "spring", stiffness: 300 }}
              >
                <Clock className="w-6 h-6 text-blue-500 mr-3 mt-1 flex-shrink-0" />
                <p className="text-gray-700">
                  Time-consuming manual processing and classification of emails
                </p>
              </motion.div>
              <motion.div 
                className="flex items-start"
                whileHover={{ x: 5 }}
                transition={{ type: "spring", stiffness: 300 }}
              >
                <AlertTriangle className="w-6 h-6 text-blue-500 mr-3 mt-1 flex-shrink-0" />
                <p className="text-gray-700">
                  Risk of missing critical updates and deadlines
                </p>
              </motion.div>
            </div>
          </motion.div>

          <motion.div
            initial={{ x: 50, opacity: 0 }}
            animate={isInView ? { x: 0, opacity: 1 } : {}}
            transition={{ delay: 0.8, duration: 0.8 }}
            className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 shadow-xl hover:shadow-2xl transition-shadow duration-300"
          >
            <h2 className="text-2xl font-semibold bg-gradient-to-r from-purple-600 to-indigo-600 text-transparent bg-clip-text mb-6">
              2024-2025 Vision
            </h2>
            <div className="space-y-6">
              <motion.div 
                className="flex items-start"
                whileHover={{ x: 5 }}
                transition={{ type: "spring", stiffness: 300 }}
              >
                <Bot className="w-6 h-6 text-purple-500 mr-3 mt-1 flex-shrink-0" />
                <p className="text-gray-700">
                  Advanced AI-powered classification with 99% accuracy
                </p>
              </motion.div>
              <motion.div 
                className="flex items-start"
                whileHover={{ x: 5 }}
                transition={{ type: "spring", stiffness: 300 }}
              >
                <Mail className="w-6 h-6 text-purple-500 mr-3 mt-1 flex-shrink-0" />
                <p className="text-gray-700">
                  Automated labeling and processing of registration-related emails
                </p>
              </motion.div>
              <motion.div 
                className="flex items-start"
                whileHover={{ x: 5 }}
                transition={{ type: "spring", stiffness: 300 }}
              >
                <Clock className="w-6 h-6 text-purple-500 mr-3 mt-1 flex-shrink-0" />
                <p className="text-gray-700">
                  Save time and reduce headaches with smart automation
                </p>
              </motion.div>
            </div>
          </motion.div>
        </div>
      </motion.div>
      <ScrollIndicator />
    </div>
  );
};

const WorkflowSection = () => {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true });

  return (
    <div className="min-h-screen bg-gradient-to-br from-white via-blue-50 to-indigo-50 pt-20 p-8 flex items-center">
      <motion.div
        ref={ref}
        initial={{ opacity: 0 }}
        animate={isInView ? { opacity: 1 } : {}}
        transition={{ duration: 0.8 }}
        className="max-w-6xl mx-auto"
      >
        <h2 className="text-3xl font-bold text-blue-900 mb-8 text-center">
          How It Works
        </h2>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Email Processing Flow */}
          <div className="bg-gray-50 rounded-lg p-6 shadow-lg">
            <h3 className="text-xl font-semibold text-blue-800 mb-4">
              Email Processing Flow
            </h3>
            <div className="text-sm text-gray-600 mb-4">
              From arrival to completion, here's how we handle your emails:
            </div>
            
            <div className="space-y-4">
              <div className="flex items-center p-3 bg-blue-50 rounded-lg">
                <Mail className="w-5 h-5 text-blue-600 mr-3 flex-shrink-0" />
                <div>
                  <div className="font-medium text-blue-900">Email Received</div>
                  <div className="text-sm text-blue-700">Initial security checks and validation</div>
                </div>
              </div>
              
              <div className="flex items-center p-3 bg-purple-50 rounded-lg">
                <Settings className="w-5 h-5 text-purple-600 mr-3 flex-shrink-0" />
                <div>
                  <div className="font-medium text-purple-900">Processing</div>
                  <div className="text-sm text-purple-700">Content extraction and analysis</div>
                </div>
              </div>
              
              <div className="flex items-center p-3 bg-indigo-50 rounded-lg">
                <AlertCircle className="w-5 h-5 text-indigo-600 mr-3 flex-shrink-0" />
                <div>
                  <div className="font-medium text-indigo-900">Classification</div>
                  <div className="text-sm text-indigo-700">AI-powered categorization and labeling</div>
                </div>
              </div>
              
              <div className="flex items-center p-3 bg-green-50 rounded-lg">
                <CheckCircle className="w-5 h-5 text-green-600 mr-3 flex-shrink-0" />
                <div>
                  <div className="font-medium text-green-900">Completion</div>
                  <div className="text-sm text-green-700">Storage and integration with Airtable</div>
                </div>
              </div>
            </div>
          </div>
          
          {/* Technical Flow */}
          <div className="bg-gray-50 rounded-lg p-6 shadow-lg">
            <h3 className="text-xl font-semibold text-blue-800 mb-4">
              Technical Architecture
            </h3>
            <div className="text-sm text-gray-600 mb-4">
              Behind the scenes, our system uses multiple specialized components:
            </div>
            
            <img 
              src="/api/placeholder/600/400" 
              alt="System Architecture Diagram" 
              className="w-full h-64 object-cover rounded-lg mb-4 bg-gray-100"
            />
            
            <div className="space-y-2 text-sm text-gray-700">
              <div className="font-medium">Key Components:</div>
              <ul className="list-disc pl-5 space-y-1">
                <li>Email Monitoring Service</li>
                <li>Content Processing Engine</li>
                <li>Classification System</li>
                <li>Integration Layer</li>
                <li>Storage & Database Systems</li>
              </ul>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

const ImpactSection = () => (
  <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 pt-20 p-8 flex items-center">
    <div className="max-w-4xl mx-auto">
      <h2 className="text-3xl font-bold text-emerald-900 mb-8 text-center">
        Real-World Impact
      </h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="bg-white rounded-lg p-6 shadow-lg">
          <h3 className="text-xl font-semibold text-emerald-800 mb-4">
            Time Savings
          </h3>
          <div className="space-y-4">
            <div className="flex items-center p-3 bg-emerald-50 rounded-lg">
              <Clock className="w-5 h-5 text-emerald-600 mr-3 flex-shrink-0" />
              <div>
                <div className="font-medium text-emerald-900">Faster Processing</div>
                <div className="text-sm text-emerald-700">
                  Reduce email processing time from hours to minutes
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-lg">
          <h3 className="text-xl font-semibold text-emerald-800 mb-4">
            Better Organization
          </h3>
          <div className="space-y-4">
            <div className="flex items-center p-3 bg-emerald-50 rounded-lg">
              <CheckCircle className="w-5 h-5 text-emerald-600 mr-3 flex-shrink-0" />
              <div>
                <div className="font-medium text-emerald-900">Improved Accuracy</div>
                <div className="text-sm text-emerald-700">
                  Consistent classification and organized tracking
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
);

const NextStepsSection = () => (
  <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-100 pt-20 p-8 flex items-center">
    <div className="max-w-4xl mx-auto">
      <h2 className="text-3xl font-bold text-purple-900 mb-8 text-center">
        Next Steps
      </h2>
      
      <div className="bg-white rounded-lg p-6 shadow-lg">
        <div className="space-y-6">
          <div className="flex items-start">
            <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0">
              <span className="text-2xl text-purple-600">1</span>
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-semibold text-purple-900">Implementation</h3>
              <p className="text-gray-600">Initial setup and configuration of the system</p>
            </div>
          </div>
          
          <div className="flex items-start">
            <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0">
              <span className="text-2xl text-purple-600">2</span>
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-semibold text-purple-900">Training</h3>
              <p className="text-gray-600">Team training and system optimization</p>
            </div>
          </div>
          
          <div className="flex items-start">
            <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0">
              <span className="text-2xl text-purple-600">3</span>
            </div>
            <div className="ml-4">
              <h3 className="text-lg font-semibold text-purple-900">Expansion</h3>
              <p className="text-gray-600">Adding more features and capabilities</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
);

const DeltaPresentation = () => {
  return (
    <div className="relative bg-gradient-to-br from-blue-50 via-purple-50 to-indigo-50">
      <Header />
      <IntroSection />
      <WorkflowSection />
      <ImpactSection />
      <NextStepsSection />
    </div>
  );
};

export default DeltaPresentation;