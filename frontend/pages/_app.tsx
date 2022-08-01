import { AppProps } from "next/app";
import Head from "next/head";
import {
  AppShell,
  Avatar,
  Group,
  Header,
  MantineProvider,
  Navbar,
  NavLink,
  ThemeIcon,
  Title,
} from "@mantine/core";
import { NotificationsProvider } from "@mantine/notifications";
import {
  IconCurrencyDollar,
  IconHome,
  IconRobot,
  IconSettings,
} from "@tabler/icons";
import { useRouter } from "next/router";

const PageNav = () => {
  const router = useRouter();

  return (
    <Navbar width={{ base: 300 }} height={window.innerHeight - 60} p="xs">
      <Navbar.Section>
        <NavLink
          label="Dashboard"
          icon={
            <ThemeIcon>
              <IconHome />
            </ThemeIcon>
          }
          onClick={() => {
            router.push("/");
          }}
        />
      </Navbar.Section>
      <Navbar.Section>
        <NavLink
          label="Algorithm Manager"
          icon={
            <ThemeIcon color="orange">
              <IconRobot />
            </ThemeIcon>
          }
          onClick={() => {
            router.push("/algorithms");
          }}
        />
      </Navbar.Section>
      <Navbar.Section>
        <NavLink
          label="Buy / Sell"
          icon={
            <ThemeIcon color="teal">
              <IconCurrencyDollar />
            </ThemeIcon>
          }
          onClick={() => {
            router.push("/trade");
          }}
        />
      </Navbar.Section>
      <Navbar.Section>
        <NavLink
          label="Settings"
          icon={
            <ThemeIcon color="red">
              <IconSettings />
            </ThemeIcon>
          }
          onClick={() => {
            router.push("/settings");
          }}
        />
      </Navbar.Section>
    </Navbar>
  );
};

const PageHeader = () => (
  <Header height={60} p="xs">
    <Group
      style={{
        marginLeft: "22px",
      }}
    >
      <Avatar src="logo.svg" alt="Stonks" />
      <Title order={2}> AutoStonks </Title>
    </Group>
  </Header>
);

export default function App(props: AppProps) {
  const { Component, pageProps } = props;

  return (
    <>
      <Head>
        <title>AutoStonks</title>
        <meta name="description" content="Stonks" />
        <link rel="icon" href="/logo.svg" />
        <meta
          name="viewport"
          content="minimum-scale=1, initial-scale=1, width=device-width"
        />
      </Head>

      <MantineProvider
        withGlobalStyles
        withNormalizeCSS
        theme={{
          /** Put your mantine theme override here */
          colorScheme: "dark",
        }}
      >
        <NotificationsProvider>
          <AppShell padding="md" navbar={<PageNav />} header={<PageHeader />}>
            <Component {...pageProps} />
          </AppShell>
        </NotificationsProvider>
      </MantineProvider>
    </>
  );
}
