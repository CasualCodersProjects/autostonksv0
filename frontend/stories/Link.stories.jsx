import Link from "../components/Link";

export default {
  title: "Link",
  component: Link,
};

const Template = (args) => <Link {...args} />;

export const Default = Template.bind({});

Default.args = {
  href: "https://blog.chand1012.dev",
  children: "Chandler's Blog",
};
