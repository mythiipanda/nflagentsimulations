import { Link, NavLink } from "react-router-dom";
import { Moon, Sun, User, MessageSquare } from "lucide-react";

export default function Header({ theme, setTheme }) {
  return (
    <header className="border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-[#0a0a1f] text-black dark:text-white">
      <div className="container mx-auto px-4">
        <nav className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="text-2xl font-bold">
              NFL Analytics
            </Link>
            <div className="hidden md:flex items-center ml-16 space-x-8">
              <NavLink
                to="/draft-simulation"
                className={({ isActive }) =>
                  `text-sm font-medium hover:text-gray-600 dark:hover:text-gray-300 ${
                    isActive ? "text-blue-500 dark:text-blue-400" : ""
                  }`
                }
              >
                Draft Simulation
              </NavLink>
              <NavLink
                to="/analysis-chat"
                className={({ isActive }) =>
                  `text-sm font-medium hover:text-gray-600 dark:hover:text-gray-300 ${
                    isActive ? "text-blue-500 dark:text-blue-400" : ""
                  }`
                }
              >
                AI Chat
              </NavLink>
              <NavLink
                to="/statistics"
                className={({ isActive }) =>
                  `text-sm font-medium hover:text-gray-600 dark:hover:text-gray-300 ${
                    isActive ? "text-blue-500 dark:text-blue-400" : ""
                  }`
                }
              >
                Statistics
              </NavLink>
              <NavLink
                to="/about"
                className={({ isActive }) =>
                  `text-sm font-medium hover:text-gray-600 dark:hover:text-gray-300 ${
                    isActive ? "text-blue-500 dark:text-blue-400" : ""
                  }`
                }
              >
                About
              </NavLink>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
              className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700"
              aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
            >
              {theme === "dark" ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
            </button>
            <button
              className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700"
              aria-label="Messages"
            >
              <MessageSquare className="h-5 w-5" />
            </button>
            <Link
              to="/get-started"
              className="px-4 py-2 rounded-full bg-white dark:bg-gray-800 text-black dark:text-white hover:bg-gray-100 dark:hover:bg-gray-700"
            >
              Get Started
            </Link>
            <button
              className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700"
              aria-label="User account"
            >
              <User className="h-5 w-5" />
            </button>
          </div>
        </nav>
      </div>
    </header>
  );
}