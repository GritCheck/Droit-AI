import type { Metadata } from 'next';

import { CONFIG } from 'src/global-config';
import { _userList } from 'src/_mock/_user';

import { UserEditView } from 'src/sections/user/view';

type Props = {
  params: Promise<{ id: string }>;
};

// Metadata must now await params
export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;

  return {
    title: `User ${id} Edit | Dashboard - ${CONFIG.appName}`,
  };
}

export default async function Page({ params }: Props) {
  // NEXT.JS 16 FIX: Must await params before destructuring
  const { id } = await params;

  const currentUser = _userList.find((user) => user.id === id);

  return <UserEditView user={currentUser} />;
}
