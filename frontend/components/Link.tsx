import Link from "next/link";
import { Button } from "@mantine/core";

export interface LinkProps {
  href: string;
  children: React.ReactNode;
}

const L = ({ href, children }: LinkProps) => {
  return (
    <Link href={href} passHref>
      <Button component="a">{children}</Button>
    </Link>
  );
};

export default L;
