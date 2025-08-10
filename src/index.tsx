import { useEffect, useState } from "react";
import { FaClipboardList } from "react-icons/fa";
import remarkHtml from "remark-html";
import remarkParse from "remark-parse";
import remarkGfm from "remark-gfm";
import { unified } from "unified";
import { patchPartnerEventStore } from "./PartnerEventStorePatch";
import {
  staticClasses,
  PanelSection,
  PanelSectionRow,
  ButtonItem,
  Field,
  SteamSpinner,
} from "@decky/ui";
import { definePlugin } from "@decky/api";
import { fetchReleases } from "./FetchReleases";

function Content() {
  const [changelogHtml, setChangelogHtml] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);

  const fetchChangelog = async (signal?: AbortSignal) => {
    try {
      const generator = fetchReleases(signal);
      const iterator = await generator.next();

      if (!iterator || iterator.done) {
        setError("An unknown error occurred while fetching the changelog.");
        return;
      }

      const html = await unified()
        .use(remarkParse)
        .use(remarkGfm)
        .use(remarkHtml)
        .process(iterator.value.body);

      setChangelogHtml(html.value as string);
      setError(null);
    } catch (err) {
      if (err instanceof DOMException && err.name === "AbortError") return;
      const errorMessage =
        err instanceof Error
          ? err.message
          : "An unknown error occurred while fetching the changelog.";
      setError(errorMessage);
    }
  };

  useEffect(() => {
    const controller = new AbortController();
    fetchChangelog(controller.signal);

    return () => {
      controller.abort();
    };
  }, []);

  const refreshChangelog = async () => {
    setIsRefreshing(true);
    setChangelogHtml(null);
    setError(null);

    try {
      await fetchChangelog();
    } finally {
      setIsRefreshing(false);
    }
  };

  return (
    <PanelSection title="Bazzite Release Notes">
      <PanelSectionRow>
        <ButtonItem
          layout="below"
          onClick={() =>
            window.open(
              "https://github.com/ublue-os/bazzite/releases",
              "_blank"
            )
          }
        >
          View All Release Notes
        </ButtonItem>
      </PanelSectionRow>
      <PanelSectionRow>
        <ButtonItem
          layout="below"
          disabled={isRefreshing}
          onClick={refreshChangelog}
        >
          {isRefreshing ? "Refreshing..." : "Refresh"}
        </ButtonItem>
      </PanelSectionRow>
      <PanelSectionRow>
        {error ? (
          <Field label="Error">{error}</Field>
        ) : changelogHtml ? (
          <Field>
            <div
              dangerouslySetInnerHTML={{
                __html: changelogHtml,
              }}
            />
          </Field>
        ) : (
          <SteamSpinner />
        )}
      </PanelSectionRow>
    </PanelSection>
  );
}

// noinspection JSUnusedGlobalSymbols
export default definePlugin(() => {
  const patches = patchPartnerEventStore();

  return {
    name: "Bazzite Changelog Viewer",
    title: <div className={staticClasses.Title}>Bazzite Buddy</div>,
    icon: <FaClipboardList/>,
    content: <Content/>,
    onDismount() {
      patches.forEach(patch => {
        patch.unpatch();
      });
    },
  };
});
