import Link from 'next/link';

export default function Home() {
  return (
    <div>
      <h1>Welcome</h1>
      <nav>
        <Link href="/create-user">Signup</Link>
        <br />
        <Link href="/signin">Login</Link>
      </nav>
    </div>
  );
}
