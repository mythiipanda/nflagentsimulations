import { Link, NavLink } from "react-router-dom";
import { Moon, Sun, User, MessageSquare } from "lucide-react";

export default function Header({ theme, setTheme }) {
  return (
    <header className="border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-[#0a0a1f] text-black dark:text-white">
      <div className="container mx-auto px-4 py-4">
        <nav className="flex items-center justify-between">
          <div className="flex items-center">
            <Link to="/" className="text-2xl font-bold text-blue-500">
              NFL Insights
            </Link>
            <div className="hidden md:flex items-center ml-10 space-x-10">s
              <NavLink
                to="/draft-simulation"
                className={({ isActive }) =>
                  `text-lg font-medium hover:text-gray-600 dark:hover:text-gray-300 ${
                    isActive ? "text-blue-500 dark:text-blue-400" : ""
                  }`
                }
              >
                Draft Simulation
              </NavLink>
              <NavLink
                to="/analysis-chat"
                className={({ isActive }) =>
                  `text-lg font-medium hover:text-gray-600 dark:hover:text-gray-300 ${
                    isActive ? "text-blue-500 dark:text-blue-400" : ""
                  }`
                }
              >
                AI Chat
              </NavLink>
              <NavLink
                to="/statistics"
                className={({ isActive }) =>
                  `text-lg font-medium hover:text-gray-600 dark:hover:text-gray-300 ${
                    isActive ? "text-blue-500 dark:text-blue-400" : ""
                  }`
                }
              >
                Statistics
              </NavLink>
              <NavLink
                to="/about"
                className={({ isActive }) =>
                  `text-lg font-medium hover:text-gray-600 dark:hover:text-gray-300 ${
                    isActive ? "text-blue-500 dark:text-blue-400" : ""
                  }`
                }
              >
                About
              </NavLink>
            </div>
          </div>
          <div className="flex items-center space-x-6">
            <button
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
              className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700"
              aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
            >
              {theme === "dark" ? (
                <Sun className="h-5 w-5 text-yellow-500" />
              ) : (
                <Moon className="h-5 w-5 text-gray-400" />
              )}
            </button>
            <button
              className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700"
              aria-label="Messages"
            >
              <MessageSquare className="h-5 w-5 text-blue-500" />
            </button>
            <Link
              to="/get-started"
              className="px-4 py-2 rounded-full bg-blue-500 text-white hover:bg-blue-600"
            >
              Get Started
            </Link>
            <button
              className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700"
              aria-label="User account"
            >
              <User className="h-5 w-5 text-gray-600 dark:text-gray-300" />
            </button>
          </div>
        </nav>
      </div>
    </header>
  );
}
