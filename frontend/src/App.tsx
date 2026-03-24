import { useState } from "react";
import { api } from "./api/client";
import type { PresentationDetail } from "./api/types";
import PresentationList from "./components/PresentationList";
import SlideViewer from "./components/SlideViewer";

export default function App() {
  const [presentation, setPresentation] = useState<PresentationDetail | null>(null);

  function handleSelect(id: number) {
    api.getPresentation(id).then(setPresentation);
  }

  if (presentation) {
    return (
      <SlideViewer
        presentation={presentation}
        onBack={() => setPresentation(null)}
      />
    );
  }

  return <PresentationList onSelect={handleSelect} />;
}
