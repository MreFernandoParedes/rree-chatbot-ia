import React, { useEffect, useState } from "react";
import ReactDOM from "react-dom/client";
import { createHashRouter, RouterProvider } from "react-router-dom";
import { I18nextProvider } from "react-i18next";
import { HelmetProvider } from "react-helmet-async";
import { initializeIcons } from "@fluentui/react";
import { checkInteractionsLimit } from "./api";
import "./index.css";
import Chat from "./pages/chat/Chat";
import LayoutWrapper from "./layoutWrapper";
import i18next from "./i18n/config";
import { InteractionsLimitPage } from "./components/InteractionsLimit";

initializeIcons();

const App = () => {
    const [hasTokenLimit, setHasTokenLimit] = useState<boolean | null>(null);

    useEffect(() => {
        const fetchInteractionsLimit = async () => {
            const result = await checkInteractionsLimit();
            setHasTokenLimit(result);
        };

        fetchInteractionsLimit();
    }, []);

    if (hasTokenLimit === null) {
        return (
            <div className="spinner-container">
                <div className="spinner"></div>
            </div>
        );
    }

    const router = createHashRouter([
        {
            path: "/",
            element: <LayoutWrapper />,
            children: hasTokenLimit
                ? [
                      {
                          index: true,
                          element: <Chat />
                      },
                      {
                          path: "*",
                          lazy: () => import("./pages/NoPage")
                      }
                  ]
                : [
                    {
                        index: true,
                        element: <InteractionsLimitPage />
                    },
                    {
                        path: "*",
                        lazy: () => import("./pages/NoPage")
                    }
                ]
        }
    ]);

    // const router = createHashRouter([
    //     {
    //         path: "/",
    //         element: <LayoutWrapper />,
    //         children:[
    //                   {
    //                       index: true,
    //                       element: <Chat />
    //                   },
    //                   {
    //                       path: "qa",
    //                       lazy: () => import("./pages/ask/Ask")
    //                   },
    //                   {
    //                       path: "*",
    //                       lazy: () => import("./pages/NoPage")
    //                   }
    //               ]
    //     }
    // ]);

    return (
        <I18nextProvider i18n={i18next}>
            <HelmetProvider>
                <RouterProvider router={router} />
            </HelmetProvider>
        </I18nextProvider>
    );
};

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
    <React.StrictMode>
        <App />
    </React.StrictMode>
);